<script setup>
import { ref } from 'vue'

const city = ref('')
const searchedCity = ref('')
const stays = ref([])
const loading = ref(false)
const error = ref('')
const validationMessage = ref('')
const hasSearched = ref(false)

const money = new Intl.NumberFormat('en-US', {
  style: 'currency',
  currency: 'USD',
  maximumFractionDigits: 0,
})

async function search() {
  const query = city.value.trim()
  validationMessage.value = ''
  error.value = ''

  if (!query) {
    validationMessage.value = 'Enter a city to search.'
    hasSearched.value = false
    stays.value = []
    return
  }

  loading.value = true
  hasSearched.value = false
  try {
    const response = await fetch(`/api/stays?city=${encodeURIComponent(query)}`)
    if (!response.ok) throw new Error('Search request failed')
    stays.value = await response.json()
    searchedCity.value = query
    hasSearched.value = true
  } catch {
    error.value = 'We could not load stays. Make sure the backend is running and try again.'
    stays.value = []
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <main>
    <section class="hero" aria-labelledby="page-title">
      <p class="eyebrow">EXPEDIA LITE</p>
      <h1 id="page-title">Find your next city stay</h1>
      <p class="intro">Search our classroom travel data for hotel stays with fixed dates and clear prices.</p>

      <form class="search" @submit.prevent="search">
        <label for="city">City</label>
        <div class="search-row">
          <input id="city" v-model="city" type="text" placeholder="Try Boston" autocomplete="address-level2" />
          <button type="submit" :disabled="loading">{{ loading ? 'Searching…' : 'Search' }}</button>
        </div>
        <p v-if="validationMessage" class="message validation" role="alert">{{ validationMessage }}</p>
      </form>
    </section>

    <section class="results" aria-live="polite" aria-busy="loading">
      <p v-if="error" class="message error" role="alert">{{ error }}</p>

      <template v-else-if="hasSearched && stays.length">
        <div class="results-heading">
          <div>
            <p class="eyebrow">SEARCH RESULTS</p>
            <h2>Hotel stays in {{ stays[0].city }}</h2>
          </div>
          <p class="count">{{ stays.length }} {{ stays.length === 1 ? 'stay' : 'stays' }}</p>
        </div>

        <div class="table-wrap">
          <table>
            <caption class="sr-only">Hotel stays matching {{ searchedCity }}</caption>
            <thead>
              <tr>
                <th scope="col">Trip</th>
                <th scope="col">Hotel</th>
                <th scope="col">Check-in</th>
                <th scope="col">Check-out</th>
                <th scope="col">Nights</th>
                <th scope="col">Nightly rate</th>
                <th scope="col">Stay price</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="stay in stays" :key="stay.trip_id">
                <td><strong>{{ stay.trip_name }}</strong><span>{{ stay.trip_id }}</span></td>
                <td>{{ stay.hotel_name }}</td>
                <td>{{ stay.check_in }}</td>
                <td>{{ stay.check_out }}</td>
                <td>{{ stay.nights }}</td>
                <td>{{ money.format(stay.nightly_rate_usd) }}</td>
                <td><strong>{{ money.format(stay.stay_price_usd) }}</strong></td>
              </tr>
            </tbody>
          </table>
        </div>
      </template>

      <div v-else-if="hasSearched" class="empty-state">
        <p class="empty-icon" aria-hidden="true">⌁</p>
        <h2>No stays found</h2>
        <p>We found no hotel stays in “{{ searchedCity }}.” Check the spelling or try another city.</p>
      </div>

      <div v-else-if="!loading && !validationMessage" class="starting-state">
        <p>Popular sample searches</p>
        <button v-for="sample in ['Boston', 'New York', 'Philadelphia']" :key="sample" @click="city = sample; search()">
          {{ sample }}
        </button>
      </div>
    </section>
  </main>
</template>
