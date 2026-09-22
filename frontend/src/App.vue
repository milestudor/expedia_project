<script setup>
import { computed, onMounted, ref } from 'vue'

const query = ref('')
const searchedQuery = ref('')
const stays = ref([])
const users = ref([])
const bookings = ref([])
const selectedUser = ref('U001')
const loading = ref(false)
const historyLoading = ref(false)
const error = ref('')
const notice = ref('')
const validationMessage = ref('')
const hasSearched = ref(false)

const money = new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 })
const activeBookings = computed(() => bookings.value.filter((booking) => booking.status === 'confirmed').length)

async function request(url, options) {
  const response = await fetch(url, options)
  if (!response.ok) throw new Error('Request failed')
  return response.status === 204 ? null : response.json()
}

async function search() {
  const value = query.value.trim()
  validationMessage.value = ''
  error.value = ''
  notice.value = ''
  if (!value) {
    validationMessage.value = 'Enter a hotel name or city to search.'
    hasSearched.value = false
    stays.value = []
    return
  }
  loading.value = true
  hasSearched.value = false
  try {
    stays.value = await request(`/api/stays?q=${encodeURIComponent(value)}`)
    searchedQuery.value = value
    hasSearched.value = true
  } catch {
    error.value = 'We could not load stays. Make sure the backend is running and try again.'
  } finally {
    loading.value = false
  }
}

async function loadHistory() {
  historyLoading.value = true
  try {
    bookings.value = await request('/api/bookings')
  } catch {
    error.value = 'We could not load booking history.'
  } finally {
    historyLoading.value = false
  }
}

async function book(stay) {
  error.value = ''
  notice.value = ''
  try {
    const booking = await request('/api/bookings', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_id: selectedUser.value, trip_id: stay.trip_id }),
    })
    notice.value = `Booking ${booking.booking_id} confirmed for ${booking.hotel_name}.`
    await loadHistory()
    document.querySelector('#booking-history')?.scrollIntoView({ behavior: 'smooth' })
  } catch {
    error.value = 'We could not create that booking. Please try again.'
  }
}

async function cancelBooking(booking) {
  error.value = ''
  try {
    await request(`/api/bookings/${booking.booking_id}`, {
      method: 'PATCH', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ status: 'cancelled' }),
    })
    notice.value = `Booking ${booking.booking_id} was cancelled and kept in your history.`
    await loadHistory()
  } catch {
    error.value = 'We could not cancel that booking.'
  }
}

async function deleteBooking(booking) {
  error.value = ''
  try {
    await request(`/api/bookings/${booking.booking_id}`, { method: 'DELETE' })
    notice.value = `Test booking ${booking.booking_id} was permanently deleted.`
    await loadHistory()
  } catch {
    error.value = 'We could not delete that booking.'
  }
}

onMounted(async () => {
  try {
    ;[users.value, bookings.value] = await Promise.all([request('/api/users'), request('/api/bookings')])
    selectedUser.value = users.value[0]?.user_id ?? ''
  } catch {
    error.value = 'We could not connect to Expedia Lite. Make sure the backend is running.'
  }
})
</script>

<template>
  <header class="topbar">
    <a href="#page-title">Expedia Lite</a><a href="#booking-history">Booking history <span>{{ activeBookings }}</span></a>
  </header>
  <main>
    <section
      class="hero"
      aria-labelledby="page-title"
    >
      <p class="eyebrow">
        SEARCH · BOOK · MANAGE
      </p>
      <h1 id="page-title">
        A lighter way to plan your next stay.
      </h1>
      <p class="intro">
        Find a hotel by name or city, make a simulated booking, and manage it from one place.
      </p>
      <form
        class="search"
        @submit.prevent="search"
      >
        <label for="query">Hotel name or city</label>
        <div class="search-row">
          <input
            id="query"
            v-model="query"
            type="search"
            placeholder="Try Harbor Lantern or Boston"
          ><button
            type="submit"
            :disabled="loading"
          >
            {{ loading ? 'Searching…' : 'Search stays' }}
          </button>
        </div>
        <p
          v-if="validationMessage"
          class="message validation"
          role="alert"
        >
          {{ validationMessage }}
        </p>
      </form>
    </section>

    <div
      class="alerts"
      aria-live="polite"
    >
      <p
        v-if="error"
        class="message error"
        role="alert"
      >
        {{ error }}
      </p>
      <p
        v-if="notice"
        class="message success"
      >
        {{ notice }}
      </p>
    </div>

    <section
      class="results"
      aria-live="polite"
      :aria-busy="loading"
    >
      <template v-if="hasSearched && stays.length">
        <div class="results-heading">
          <div>
            <p class="eyebrow">
              AVAILABLE STAYS
            </p><h2>Results for “{{ searchedQuery }}”</h2>
          </div><p class="count">
            {{ stays.length }} {{ stays.length === 1 ? 'stay' : 'stays' }}
          </p>
        </div>
        <div class="booking-user">
          <label for="traveler">Book for</label><select
            id="traveler"
            v-model="selectedUser"
          >
            <option
              v-for="user in users"
              :key="user.user_id"
              :value="user.user_id"
            >
              {{ user.name }} · {{ user.email }}
            </option>
          </select>
        </div>
        <div class="table-wrap">
          <table>
            <caption class="sr-only">
              Hotel stays matching {{ searchedQuery }}
            </caption><thead><tr><th>Stay</th><th>Hotel</th><th>Dates</th><th>Nights</th><th>Price</th><th><span class="sr-only">Booking action</span></th></tr></thead><tbody>
              <tr
                v-for="stay in stays"
                :key="stay.trip_id"
              >
                <td><strong>{{ stay.trip_name }}</strong><span>{{ stay.trip_id }}</span></td><td>{{ stay.hotel_name }}<span>{{ stay.city }}, {{ stay.state }}</span></td><td>{{ stay.check_in }}<span>to {{ stay.check_out }}</span></td><td>{{ stay.nights }}</td><td><strong>{{ money.format(stay.stay_price_usd) }}</strong><span>{{ money.format(stay.nightly_rate_usd) }}/night</span></td><td>
                  <button
                    class="action primary"
                    @click="book(stay)"
                  >
                    Book
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </template>
      <div
        v-else-if="hasSearched"
        class="empty-state"
      >
        <p
          class="empty-icon"
          aria-hidden="true"
        >
          ⌁
        </p><h2>No stays found</h2><p>We found no hotels matching “{{ searchedQuery }}.” Check the spelling or try a city.</p>
      </div>
      <div
        v-else-if="!loading && !validationMessage"
        class="starting-state"
      >
        <p>Explore sample searches</p><button
          v-for="sample in ['Harbor Lantern', 'New York', 'Philadelphia']"
          :key="sample"
          @click="query = sample; search()"
        >
          {{ sample }}
        </button>
      </div>
    </section>

    <section
      id="booking-history"
      class="history"
      aria-labelledby="history-title"
    >
      <div class="results-heading">
        <div>
          <p class="eyebrow">
            SAVED IN SQLITE
          </p><h2 id="history-title">
            Booking history
          </h2>
        </div><p class="count">
          {{ bookings.length }} total
        </p>
      </div>
      <p class="section-copy">
        Cancelled bookings stay in history. Use Delete only for a test booking you no longer need.
      </p>
      <p v-if="historyLoading">
        Refreshing history…
      </p>
      <div
        v-else-if="bookings.length"
        class="booking-grid"
      >
        <article
          v-for="booking in bookings"
          :key="booking.booking_id"
          class="booking-card"
        >
          <div class="card-top">
            <span :class="['status', booking.status]">{{ booking.status }}</span><strong>{{ booking.booking_id }}</strong>
          </div>
          <h3>{{ booking.hotel_name }}</h3><p>{{ booking.trip_name }}</p>
          <dl><div><dt>Traveler</dt><dd>{{ booking.user_name }}</dd></div><div><dt>Dates</dt><dd>{{ booking.check_in }} – {{ booking.check_out }}</dd></div><div><dt>Total</dt><dd>{{ money.format(booking.total_price_usd) }}</dd></div></dl>
          <div class="card-actions">
            <button
              v-if="booking.status === 'confirmed'"
              class="action secondary"
              @click="cancelBooking(booking)"
            >
              Cancel booking
            </button><button
              class="action danger"
              @click="deleteBooking(booking)"
            >
              Delete test booking
            </button>
          </div>
        </article>
      </div>
      <div
        v-else
        class="empty-state compact"
      >
        <h3>No bookings yet</h3><p>Search for a stay and select Book to add one.</p>
      </div>
    </section>
  </main>
</template>
