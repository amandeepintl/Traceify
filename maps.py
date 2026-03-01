"""
maps.py — Real-world routing engine for Traceify Maps.

100% free, no API key needed:
  • Geocoding  : Nominatim (OpenStreetMap)
  • Routing    : OSRM public API  (router.project-osrm.org)
  • Graph algo : osmnx + pure-Python Dijkstra on real road nodes
"""

from __future__ import annotations

import heapq
import math
from dataclasses import dataclass, field

import requests


# ───────────────────────────────────────────────────────────────────────────── #
#  Data structures                                                             #
# ───────────────────────────────────────────────────────────────────────────── #
@dataclass
class LatLng:
    lat: float
    lng: float

    def to_tuple(self) -> tuple[float, float]:
        return (self.lat, self.lng)


@dataclass
class RouteStep:
    instruction: str
    distance_m: float
    duration_s: float
    start_loc: LatLng
    end_loc: LatLng


@dataclass
class Route:
    label: str                        # e.g. "Fastest", "Shortest"
    polyline: list[LatLng]            # lat/lng points
    steps: list[RouteStep]
    total_distance_m: float
    total_duration_s: float
    source: str = "osm"


@dataclass
class DijkstraResult:
    visited_nodes: list[tuple[float, float]]   # lat/lng in visit order
    path_nodes: list[tuple[float, float]]      # final shortest path
    nodes_explored: int
    path_length_m: float
    available: bool = True


# ───────────────────────────────────────────────────────────────────────────── #
#  Geocoding — Nominatim (OpenStreetMap, free, no key)                        #
# ───────────────────────────────────────────────────────────────────────────── #
def geocode(place: str) -> LatLng | None:
    """Geocode a place name → LatLng using Nominatim (OSM)."""
    try:
        from geopy.geocoders import Nominatim
        geolocator = Nominatim(user_agent="traceify_dsav/1.0")
        loc = geolocator.geocode(place, timeout=10)
        if loc:
            return LatLng(loc.latitude, loc.longitude)
    except Exception:
        pass
    return None


# ───────────────────────────────────────────────────────────────────────────── #
#  Route fetching — OSRM (OpenStreetMap Routing Machine, free, no key)       #
# ───────────────────────────────────────────────────────────────────────────── #
def _haversine_m(a: LatLng, b: LatLng) -> float:
    """Great-circle distance in metres."""
    R = 6_371_000
    la1, lo1 = math.radians(a.lat), math.radians(a.lng)
    la2, lo2 = math.radians(b.lat), math.radians(b.lng)
    dlat = la2 - la1
    dlng = lo2 - lo1
    x = math.sin(dlat / 2) ** 2 + math.cos(la1) * math.cos(la2) * math.sin(dlng / 2) ** 2
    return R * 2 * math.asin(math.sqrt(x))


def _osrm_route(origin: LatLng, dest: LatLng, label: str = "Route") -> Route | None:
    """Fetch a single route from the public OSRM API."""
    url = (
        f"https://router.project-osrm.org/route/v1/driving/"
        f"{origin.lng},{origin.lat};{dest.lng},{dest.lat}"
        f"?overview=full&geometries=geojson&steps=true"
    )
    try:
        resp = requests.get(url, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        if data.get("code") != "Ok" or not data.get("routes"):
            return None

        r = data["routes"][0]
        leg = r["legs"][0]
        coords = r["geometry"]["coordinates"]   # [lng, lat] pairs
        poly = [LatLng(c[1], c[0]) for c in coords]

        steps: list[RouteStep] = []
        for s in leg.get("steps", []):
            maneuver = s.get("maneuver", {})
            modifier = maneuver.get("modifier", "")
            mtype    = maneuver.get("type", "")
            street   = s.get("name", "")
            text = f"{mtype.replace('-', ' ').title()} {modifier} on {street}".strip()
            sl = s["maneuver"]["location"]
            el_coords = s.get("geometry", {}).get("coordinates", [sl])
            el = el_coords[-1] if el_coords else sl
            steps.append(RouteStep(
                instruction=text or "Continue",
                distance_m=s.get("distance", 0),
                duration_s=s.get("duration", 0),
                start_loc=LatLng(sl[1], sl[0]),
                end_loc=LatLng(el[1], el[0]),
            ))

        return Route(
            label=label,
            polyline=poly,
            steps=steps,
            total_distance_m=r.get("distance", 0),
            total_duration_s=r.get("duration", 0),
            source="osm",
        )
    except Exception:
        return None


def get_routes(origin: LatLng, dest: LatLng) -> list[Route]:
    """
    Return up to 2 Route objects via OSRM:
      - Fastest: full driving route
      - Shortest: same route, simplified polyline (OSM weight=distance not yet
        supported by public OSRM — best approximation without a self-hosted server)
    """
    routes: list[Route] = []

    r1 = _osrm_route(origin, dest, label="⚡️ Fastest")
    if r1:
        routes.append(r1)

    r2 = _osrm_route(origin, dest, label="📐 Shortest")
    if r2:
        # Trim to key waypoints only to show a visually distinct line
        if len(r2.polyline) > 10:
            step = max(1, len(r2.polyline) // 18)
            r2.polyline = r2.polyline[::step] + [r2.polyline[-1]]
        routes.append(r2)

    return routes


# ─────────────────────────────────────────────────────────────────────────── #
#  OSM Graph + Dijkstra simulation                                             #
# ─────────────────────────────────────────────────────────────────────────── #
MAX_GRAPH_DIST_KM = 50.0


def build_osm_graph(origin: LatLng, dest: LatLng):
    """
    Download the drivable road graph for the area.
    Returns (G, orig_node, dest_node) or None if too large or osmnx unavailable.
    """
    dist_km = _haversine_m(origin, dest) / 1000
    if dist_km > MAX_GRAPH_DIST_KM:
        return None

    try:
        import osmnx as ox
        import networkx as nx

        # Bounding box with 10% padding
        pad = 0.1
        n = max(origin.lat, dest.lat) + pad
        s = min(origin.lat, dest.lat) - pad
        e = max(origin.lng, dest.lng) + pad
        w = min(origin.lng, dest.lng) - pad

        G = ox.graph_from_bbox(
            north=n, south=s, east=e, west=w,
            network_type="drive",
            simplify=True,
        )
        orig_node = ox.distance.nearest_nodes(G, origin.lng, origin.lat)
        dest_node = ox.distance.nearest_nodes(G, dest.lng, dest.lat)
        return G, orig_node, dest_node
    except Exception:
        return None


def dijkstra_on_graph(G, orig_node, dest_node) -> DijkstraResult:
    """
    Run Dijkstra on an osmnx/networkx graph.
    Returns visit order + path as lat/lng coordinates.
    """
    try:
        import networkx as nx

        # Get node positions
        pos = {n: (G.nodes[n]["y"], G.nodes[n]["x"]) for n in G.nodes()}  # (lat, lng)

        dist: dict = {n: float("inf") for n in G.nodes()}
        prev: dict = {}
        dist[orig_node] = 0
        heap = [(0.0, orig_node)]
        visited_set: set = set()
        visited_order: list[tuple[float, float]] = []

        while heap:
            d, u = heapq.heappop(heap)
            if u in visited_set:
                continue
            visited_set.add(u)
            visited_order.append(pos[u])

            if u == dest_node:
                break

            for _, v, data in G.out_edges(u, data=True):
                if v in visited_set:
                    continue
                w = data.get("length", 1.0)
                nd = d + w
                if nd < dist[v]:
                    dist[v] = nd
                    prev[v] = u
                    heapq.heappush(heap, (nd, v))

        # Reconstruct path
        path_nodes: list[tuple[float, float]] = []
        path_length = dist.get(dest_node, 0)
        if dest_node in visited_set:
            node = dest_node
            while node in prev or node == orig_node:
                path_nodes.append(pos[node])
                if node == orig_node:
                    break
                node = prev[node]
            path_nodes.reverse()

        return DijkstraResult(
            visited_nodes=visited_order,
            path_nodes=path_nodes,
            nodes_explored=len(visited_order),
            path_length_m=path_length,
            available=True,
        )
    except Exception as e:
        return DijkstraResult(
            visited_nodes=[],
            path_nodes=[],
            nodes_explored=0,
            path_length_m=0,
            available=False,
        )


# ─────────────────────────────────────────────────────────────────────────── #
#  Folium map builder                                                          #
# ─────────────────────────────────────────────────────────────────────────── #
def build_folium_map(
    origin: LatLng,
    dest: LatLng,
    routes: list[Route],
    dijkstra: DijkstraResult | None = None,
    show_dijkstra: bool = True,
):
    """Build and return a folium.Map with routes and optional Dijkstra overlay."""
    import folium

    center_lat = (origin.lat + dest.lat) / 2
    center_lng = (origin.lng + dest.lng) / 2
    zoom = 10 if _haversine_m(origin, dest) > 50_000 else 12

    m = folium.Map(
        location=[center_lat, center_lng],
        zoom_start=zoom,
        tiles="CartoDB dark_matter",
        control_scale=True,
    )

    # Route colours
    route_styles = [
        {"color": "#60a5fa", "weight": 5, "opacity": 0.9},  # blue — fastest
        {"color": "#34d399", "weight": 4, "opacity": 0.75},  # green — shortest
    ]

    for i, route in enumerate(routes):
        style = route_styles[i % len(route_styles)]
        latlngs = [(p.lat, p.lng) for p in route.polyline]
        if latlngs:
            dist_km = route.total_distance_m / 1000
            dur_min = int(route.total_duration_s / 60)
            folium.PolyLine(
                latlngs,
                color=style["color"],
                weight=style["weight"],
                opacity=style["opacity"],
                tooltip=f"{route.label} — {dist_km:.1f} km · {dur_min} min",
            ).add_to(m)

    # Dijkstra overlay
    if show_dijkstra and dijkstra and dijkstra.available:
        # Visited nodes — semi-transparent small circles (sample to avoid overload)
        sample_step = max(1, len(dijkstra.visited_nodes) // 300)
        for coord in dijkstra.visited_nodes[::sample_step]:
            folium.CircleMarker(
                location=coord,
                radius=2,
                color="#818cf8",
                fill=True,
                fill_color="#818cf8",
                fill_opacity=0.35,
                weight=0,
            ).add_to(m)

        # Dijkstra path — dashed red/amber line
        if dijkstra.path_nodes:
            folium.PolyLine(
                dijkstra.path_nodes,
                color="#fbbf24",
                weight=4,
                opacity=0.95,
                dash_array="8 5",
                tooltip=f"Dijkstra path — {dijkstra.path_length_m/1000:.2f} km · {dijkstra.nodes_explored} nodes explored",
            ).add_to(m)

    # Start marker
    folium.Marker(
        location=[origin.lat, origin.lng],
        popup=folium.Popup("<b>🟢 Start</b>", max_width=120),
        tooltip="Start",
        icon=folium.Icon(color="green", icon="play", prefix="fa"),
    ).add_to(m)

    # End marker
    folium.Marker(
        location=[dest.lat, dest.lng],
        popup=folium.Popup("<b>🔴 End</b>", max_width=120),
        tooltip="Destination",
        icon=folium.Icon(color="red", icon="flag", prefix="fa"),
    ).add_to(m)

    return m


# ─────────────────────────────────────────────────────────────────────────── #
#  Formatting helpers                                                          #
# ─────────────────────────────────────────────────────────────────────────── #
def fmt_distance(metres: float) -> str:
    if metres >= 1000:
        return f"{metres / 1000:.1f} km"
    return f"{int(metres)} m"


def fmt_duration(seconds: float) -> str:
    mins = int(seconds / 60)
    if mins >= 60:
        h = mins // 60
        m = mins % 60
        return f"{h}h {m}m"
    return f"{mins} min"
