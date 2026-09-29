<script setup>
import { nextTick, ref } from 'vue'
import HotelMap from './HotelMap.vue'

const postcode = ref('')
const state = ref('idle')
const message = ref('')
const result = ref(null)
const selectedId = ref('')
let sequence = 0

async function search() {
  if (state.value === 'loading') return
  result.value = null
  selectedId.value = ''
  message.value = ''
  const value = postcode.value.trim()
  if (!/^[0-9]{5}$/.test(value)) {
    state.value = 'invalid'
    message.value = 'Enter a five-digit U.S. ZIP code, such as 02108.'
    return
  }
  state.value = 'loading'
  try {
    const response = await fetch(`/api/hotels?postcode=${encodeURIComponent(value)}`)
    const body = await response.json()
    if (!response.ok) {
      state.value = response.status === 404 ? 'unresolved' : 'failed'
      message.value = typeof body.detail === 'string' ? body.detail : 'Hotel search failed. Please try again later.'
      return
    }
    result.value = body
    sequence += 1
    state.value = body.hotels.length ? 'results' : 'empty'
  } catch {
    state.value = 'failed'
    message.value = 'Hotel search failed. Check your connection and try again.'
  }
}
async function selectHotel(id, fromMap = false) {
  selectedId.value = id
  if (fromMap) {
    await nextTick()
    document.querySelector('.hotel-card.selected')?.scrollIntoView({ behavior: 'smooth', block: 'nearest' })
  }
}
</script>

<template>
  <main class="discovery">
    <header class="discovery-nav">
      <a
        href="/"
        class="brand"
      >expedia <span>lite</span><b>↗</b></a>
      <span class="project-tag">HOTEL DISCOVERY</span>
      <a href="/sample-stays">Sample stays ↗</a>
    </header>
    <section class="discovery-hero">
      <div class="hero-copy">
        <p class="kicker">
          A PLACE TO START
        </p>
        <h1>One ZIP.<br>A little closer to your next stay.</h1>
        <p>Explore hotels within 5 km of a U.S. ZIP code’s returned location.</p>
      </div>
      <form
        class="discovery-search"
        @submit.prevent="search"
      >
        <label for="hotel-zip">Where are you headed?</label>
        <div class="discovery-input-row">
          <input
            id="hotel-zip"
            v-model="postcode"
            type="text"
            inputmode="numeric"
            autocomplete="postal-code"
            placeholder="U.S. ZIP code, e.g. 02108"
            :disabled="state === 'loading'"
            :aria-invalid="state === 'invalid'"
            aria-describedby="zip-guidance"
          >
          <button
            type="submit"
            :disabled="state === 'loading'"
          >
            {{ state === 'loading' ? 'Searching…' : 'Find hotels →' }}
          </button>
        </div>
        <p id="zip-guidance">
          Five digits, including leading zeros. Search uses the ZIP’s center point, not your current location.
        </p>
      </form>
    </section>
    <section
      class="discovery-content"
      aria-label="Hotel search results"
      :aria-busy="state === 'loading'"
    >
      <div aria-live="polite">
        <div
          v-if="state === 'idle'"
          class="discovery-placeholder"
        >
          <span class="placeholder-symbol">⌖</span><h2>Your next stop starts here.</h2>
          <p>Enter a ZIP to explore hotel locations side by side on a list and map.</p>
        </div>
        <p
          v-else-if="state === 'loading'"
          class="discovery-status"
        >
          Finding your ZIP and nearby hotels…
        </p>
        <div
          v-else-if="message"
          class="discovery-error"
          role="alert"
        >
          <h2>{{ state === 'invalid' ? 'Check your ZIP code' : state === 'unresolved' ? 'ZIP code not found' : 'Search unavailable' }}</h2>
          <p>{{ message }}</p>
        </div>
        <div
          v-else-if="result"
          class="discovery-results-heading"
        >
          <div>
            <p class="kicker">
              EXPLORE THE AREA
            </p><h2>{{ result.hotels.length }} hotels returned near {{ result.center.postcode }}</h2>
            <p>{{ result.center.locality || 'U.S. postcode location' }} · Within 5 km of {{ result.center.latitude.toFixed(4) }}, {{ result.center.longitude.toFixed(4) }}</p>
          </div>
          <span class="radius-tag">5 km radius</span>
        </div>
      </div>
      <template v-if="result">
        <p class="coverage-note">
          Up to {{ result.limit }} provider results. Coverage varies; this is not a complete hotel inventory.{{ result.limit_reached ? ' The result limit was reached.' : '' }}
        </p>
        <div class="discovery-grid">
          <div class="hotel-list">
            <div
              v-if="state === 'empty'"
              class="discovery-placeholder"
            >
              <h2>No nearby hotels returned</h2><p>The ZIP was resolved, but the provider returned no hotels within 5 km. Try another ZIP.</p>
            </div>
            <button
              v-for="(hotel, index) in result.hotels"
              :key="hotel.place_id"
              class="hotel-card"
              :class="{ selected: hotel.place_id === selectedId }"
              :aria-pressed="hotel.place_id === selectedId"
              @click="selectHotel(hotel.place_id)"
            >
              <span class="hotel-number">{{ index + 1 }}</span><span class="hotel-info"><strong>{{ hotel.name || 'Hotel name unavailable' }}</strong><span>{{ hotel.address || 'Address unavailable' }}</span><small>{{ hotel.latitude.toFixed(5) }}, {{ hotel.longitude.toFixed(5) }}</small><span
                v-if="hotel.place_id === selectedId"
                class="selection-label"
              >Selected on map</span></span><span aria-hidden="true">↗</span>
            </button>
          </div>
          <HotelMap
            :key="sequence"
            :center="result.center"
            :hotels="result.hotels"
            :selected-id="selectedId"
            @select="selectHotel($event, true)"
          />
        </div>
      </template>
    </section>
    <footer class="discovery-footer">
      <span>Location discovery only. Prices and room availability are not provided.</span><a href="https://www.geoapify.com/">Powered by Geoapify</a>
    </footer>
  </main>
</template>

<style scoped>
.discovery { background: #f7f8f5; color: #15313b; }
.discovery-nav { max-width: 1280px; margin: auto; padding: 25px 40px; display: flex; gap: 25px; align-items: center; }
.discovery-nav a { text-decoration: none; font-size: 13px; }
.discovery-nav .brand { font-size: 26px; font-weight: 800; letter-spacing: -1.4px; margin-right: auto; }.brand span { font-weight: 400; }.brand b { margin-left: 10px; color: #237872; }
.project-tag { font-size: 10px; letter-spacing: 2px; color: #627579; }
.discovery-hero { padding: 45px max(40px, calc((100vw - 1200px) / 2)) 38px; background: #102f3e; color: #fff; }
.kicker { font-size: 10px; letter-spacing: 2px; font-weight: 800; margin: 0 0 14px; }.hero-copy .kicker { color: #b5d8cd; }
.hero-copy h1 { max-width: 900px; font-size: clamp(34px, 4vw, 54px); line-height: 1.12; letter-spacing: -2px; font-weight: 600; }
.hero-copy > p:last-child { color: #c4d4d6; margin: 21px 0 28px; }
.discovery-search { max-width: 760px; }.discovery-search label { display: block; font-size: 13px; font-weight: 700; margin-bottom: 10px; }
.discovery-input-row { display: flex; gap: 8px; padding: 6px; background: white; border-radius: 10px; }.discovery-input-row input { flex: 1; min-width: 0; border: none; border-radius: 6px; padding: 15px; color: #15313b; }.discovery-input-row button { border: none; border-radius: 7px; padding: 14px 26px; background: #f5ce72; color: #15313b; font-weight: 750; }
#zip-guidance { font-size: 12px; line-height: 1.5; color: #c4d4d6; margin-bottom: 0; }
.discovery-content { max-width: 1280px; margin: auto; padding: 34px 40px 44px; min-height: 340px; }.discovery-placeholder { text-align: center; padding: 54px 22px; color: #526970; }.discovery-placeholder h2 { font-size: 24px; color: #15313b; margin: 14px 0; }.discovery-placeholder p { font-size: 14px; line-height: 1.65; }.placeholder-symbol { font-size: 40px; color: #237872; }
.discovery-status { padding: 50px 0; }.discovery-error { padding: 28px; background: #fff0e9; border-radius: 12px; }.discovery-error h2 { font-size: 22px; }
.discovery-results-heading { display: flex; align-items: center; gap: 18px; justify-content: space-between; }.discovery-results-heading h2 { font-size: 26px; }.discovery-results-heading p:last-child { font-size: 13px; color: #526970; }.radius-tag { font-size: 12px; background: #e2eee7; border-radius: 20px; padding: 9px 15px; white-space: nowrap; }.coverage-note { font-size: 12px; color: #526970; margin: 4px 0 23px; }
.discovery-grid { display: grid; grid-template-columns: minmax(280px, .85fr) minmax(0, 1.25fr); gap: 24px; }.hotel-list { max-height: 480px; overflow-y: auto; padding: 3px; }.hotel-card { display: flex; align-items: flex-start; width: 100%; gap: 13px; text-align: left; padding: 20px 16px; border: 1px solid #d9e1db; border-radius: 12px; background: white; color: #15313b; margin-bottom: 10px; }.hotel-card.selected { border: 2px solid #237872; padding: 19px 15px; background: #eff6f1; }.hotel-number { display: grid; place-items: center; flex: 0 0 29px; height: 29px; border-radius: 50%; background: #eaf0eb; font-size: 12px; font-weight: 700; }.hotel-info { flex: 1; min-width: 0; }.hotel-info strong { display: block; font-size: 15px; line-height: 1.4; }.hotel-info > span { display: block; margin-top: 6px; font-size: 12px; line-height: 1.5; color: #526970; }.hotel-info small { display: block; font-size: 11px; margin-top: 9px; color: #627579; }.hotel-info .selection-label { color: #237872; font-weight: 750; }
.discovery-footer { max-width: 1200px; margin: auto; border-top: 1px solid #d9e1db; padding: 24px 0; display: flex; gap: 20px; justify-content: space-between; font-size: 11px; color: #526970; }
button:focus-visible, input:focus-visible, a:focus-visible { outline: 3px solid #d9992e; outline-offset: 3px; }button:disabled { opacity: .65; cursor: wait; }
@media(max-width: 760px) { .discovery-nav { padding: 20px; }.project-tag { display: none; }.discovery-hero { padding: 32px 20px; }.discovery-content { padding: 28px 17px; }.discovery-grid { grid-template-columns: 1fr; }.hotel-list { max-height: 350px; }.discovery-input-row { flex-direction: column; }.discovery-results-heading { align-items: flex-start; }.radius-tag { display: none; }.discovery-footer { margin: 0 20px; flex-direction: column; }.hero-copy h1 { letter-spacing: -1px; } }
</style>
