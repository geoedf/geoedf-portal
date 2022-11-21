var mapopts = {
    zoomSnap: 0.25,
};

var map = L.map("map", mapopts).setView([0, 0], 1);

var roadMutant = L.gridLayer
    .googleMutant({
        maxZoom: 24,
        type: "roadmap",
    })
    .addTo(map);

var satMutant = L.gridLayer.googleMutant({
    maxZoom: 24,
    type: "satellite",
});

var terrainMutant = L.gridLayer.googleMutant({
    maxZoom: 24,
    type: "terrain",
});

var hybridMutant = L.gridLayer.googleMutant({
    maxZoom: 24,
    type: "hybrid",
});

var styleMutant = L.gridLayer.googleMutant({
    styles: [
        {elementType: "labels", stylers: [{visibility: "off"}]},
        {featureType: "water", stylers: [{color: "#444444"}]},
        {
            featureType: "landscape",
            stylers: [{color: "#eeeeee"}]
        },
        {featureType: "road", stylers: [{visibility: "off"}]},
        {featureType: "poi", stylers: [{visibility: "off"}]},
        {
            featureType: "transit",
            stylers: [{visibility: "off"}]
        },
        {
            featureType: "administrative",
            stylers: [{visibility: "off"}]
        },
        {
            featureType: "administrative.locality",
            stylers: [{visibility: "off"}],
        },
    ],
    maxZoom: 24,
    type: "roadmap",
});

var trafficMutant = L.gridLayer.googleMutant({
    maxZoom: 24,
    type: "roadmap",
});
trafficMutant.addGoogleLayer("TrafficLayer");

var transitMutant = L.gridLayer.googleMutant({
    maxZoom: 24,
    type: "roadmap",
});
transitMutant.addGoogleLayer("TransitLayer");

var boundsStr = {};
// var boundsStr = {
// {
//     data | safe
// }
// }
// ['geo']['box'];
console.log(boundsStr);
var temp = boundsStr.trim().split(" ");
var bounds = [[temp[0], temp[1]], [temp[2], temp[3]]];

var centerLocation = [(Number(temp[0]) + Number(temp[2])) / 2, (Number(temp[1]) + Number(temp[3])) / 2];
console.log(bounds);
console.log(centerLocation);

var rectangle = L.rectangle(bounds).addTo(map);

map.fitBounds(bounds);

var grid = L.gridLayer({
    attribution: "Debug tilecoord grid",
});

L.control
    .layers(
        {
            Roadmap: roadMutant,
            Aerial: satMutant,
            Terrain: terrainMutant,
            Hybrid: hybridMutant,
            Styles: styleMutant,
            Traffic: trafficMutant,
            Transit: transitMutant,
        },
        {
            "Tilecoord grid": grid,
        },
        {
            collapsed: false,
        }
    )
    .addTo(map);