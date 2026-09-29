<script setup>
import { onBeforeUnmount, onMounted, ref, watch } from 'vue'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'

const props = defineProps({
  center: { type: Object, required: true },
  hotels: { type: Array, required: true },
  selectedId: { type: String, default: '' },
})
const emit = defineEmits(['select'])
const canvas = ref(null)
const tileError = ref(false)
let map
const markers = new Map()
const icon = (number, selected) => L.divIcon({
  className: 'hotel-marker',
  html: `<span class="map-pin${selected ? ' is-selected' : ''}">${number}</span>`,
  iconSize: [34, 34], iconAnchor: [17, 17],
})

onMounted(() => {
  const center = [props.center.latitude, props.center.longitude]
  map = L.map(canvas.value, { scrollWheelZoom: false }).setView(center, 13)
  L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
  }).on('tileerror', () => { tileError.value = true }).addTo(map)
  const circle = L.circle(center, { radius: 5000, color: '#287774', weight: 1, fillOpacity: 0.035 }).addTo(map)
  L.circleMarker(center, { radius: 5, color: '#102c51', fillOpacity: 1 }).bindTooltip('Returned ZIP search center').addTo(map)
  map.fitBounds(circle.getBounds(), { padding: [12, 12] })
  props.hotels.forEach((hotel, index) => {
    const name = hotel.name || 'Hotel name unavailable'
    const content = document.createElement('div')
    content.textContent = `${index + 1}. ${name}`
    const marker = L.marker([hotel.latitude, hotel.longitude], {
      icon: icon(index + 1, false), keyboard: true, title: `${index + 1}. ${name}`, alt: name,
    }).addTo(map).bindPopup(content)
    marker.on('click', () => emit('select', hotel.place_id))
    marker.on('keydown', (event) => {
      if (event.originalEvent.key === 'Enter' || event.originalEvent.key === ' ') {
        L.DomEvent.stop(event.originalEvent)
        emit('select', hotel.place_id)
      }
    })
    marker.getElement().setAttribute('aria-label', `${index + 1}. ${name}`)
    marker.getElement().setAttribute('aria-pressed', 'false')
    markers.set(hotel.place_id, marker)
  })
})
watch(() => props.selectedId, (id) => {
  props.hotels.forEach((hotel) => {
    const marker = markers.get(hotel.place_id)
    if (!marker) return
    marker.getElement().querySelector('.map-pin').classList.toggle('is-selected', hotel.place_id === id)
    marker.getElement().setAttribute('aria-pressed', String(hotel.place_id === id))
    marker.setZIndexOffset(hotel.place_id === id ? 1000 : 0)
    if (hotel.place_id === id) {
      map.panTo(marker.getLatLng())
      marker.openPopup()
    }
  })
})
onBeforeUnmount(() => map?.remove())
</script>

<template>
  <div class="map-frame">
    <div
      ref="canvas"
      class="hotel-map"
      aria-label="Hotels within 5 kilometers of the ZIP center"
    />
    <p
      v-if="tileError"
      class="tile-error"
      role="alert"
    >
      Map imagery could not load. Hotel markers and the list remain available. Retry the search to reload imagery.
    </p>
    <p class="map-help">
      Circle: 5 km search area · Dot: returned ZIP center. Tab to a numbered marker and press Enter to select.
    </p>
  </div>
</template>

<style>
.hotel-map { height: 480px; width: 100%; border-radius: 15px; background: #e5ece8; z-index: 0; }
.map-pin { display: grid; place-items: center; width: 34px; height: 34px; border-radius: 50%; border: 2px solid white; background: #102c51; color: white; font: 700 13px system-ui; box-shadow: 0 2px 8px #102c5155; }
.map-pin.is-selected { background: #237872; outline: 4px solid #f6cf70; }
.hotel-marker:focus-visible { outline: 4px solid #f6cf70; border-radius: 50%; }
.map-help { color: #566773; font-size: 12px; line-height: 1.5; }
.tile-error { padding: 12px; background: #fff0d9; color: #714710; }
</style>
