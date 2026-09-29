<script setup>
import { ref } from 'vue'

const postcode = ref('')
const requestedPostcode = ref('')
const loading = ref(false)
const location = ref(null)
const error = ref('')

async function lookup() {
  if (loading.value) return
  location.value = null
  error.value = ''
  const value = postcode.value.trim()
  if (!/^[0-9]{5}$/.test(value)) {
    error.value = 'Enter a five-digit U.S. ZIP code.'
    return
  }
  requestedPostcode.value = value
  loading.value = true
  try {
    const response = await fetch(`/api/demo/zip-location?postcode=${encodeURIComponent(value)}`)
    const body = await response.json()
    if (!response.ok) {
      error.value = typeof body.detail === 'string' ? body.detail : 'ZIP lookup failed. Please try again.'
      return
    }
    location.value = body
  } catch {
    error.value = 'We could not look up the ZIP. Please try again.'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <section
    class="zip-demo"
    aria-labelledby="zip-demo-title"
  >
    <h2 id="zip-demo-title">
      ZIP lookup
    </h2>
    <form @submit.prevent="lookup">
      <label for="zip-postcode">U.S. ZIP code</label>
      <div class="zip-search-row">
        <input
          id="zip-postcode"
          v-model="postcode"
          type="text"
          inputmode="numeric"
          autocomplete="postal-code"
          placeholder="e.g. 16802"
          :disabled="loading"
          aria-describedby="zip-help"
        >
        <button
          class="action zip-button"
          type="submit"
          :disabled="loading"
        >
          Look up ZIP
        </button>
      </div>
      <p id="zip-help">
        Enter a five-digit U.S. ZIP code.
      </p>
    </form>
    <div
      aria-live="polite"
      :aria-busy="loading"
    >
      <p v-if="loading">
        Looking up ZIP {{ requestedPostcode }}…
      </p>
      <p
        v-else-if="error"
        class="message error"
        role="alert"
      >
        {{ error }}
      </p>
      <dl v-else-if="location">
        <div><dt>Postcode</dt><dd>{{ location.postcode }}</dd></div>
        <div v-if="location.locality">
          <dt>Locality</dt><dd>{{ location.locality }}</dd>
        </div>
        <div><dt>Latitude</dt><dd>{{ location.latitude }}</dd></div>
        <div><dt>Longitude</dt><dd>{{ location.longitude }}</dd></div>
      </dl>
    </div>
  </section>
</template>

<style scoped>
.zip-demo { max-width: 1132px; margin: 0 auto 40px; padding: 24px; border: 1px solid #dfe4ed; border-radius: 14px; background: #fff; }
.zip-demo h2 { font-size: 1.4rem; margin-bottom: 18px; }
.zip-demo label { display: block; margin-bottom: 8px; font-weight: 700; }
.zip-search-row { display: flex; flex-wrap: wrap; gap: 10px; }
.zip-search-row input { min-width: 0; max-width: 100%; padding: 10px 12px; border: 1px solid #b9c5d6; border-radius: 8px; }
#zip-help { color: #647287; font-size: .85rem; }
.zip-button { color: #fff; border: 1px solid #174fae; background: #245fbd; }
.zip-button:disabled { opacity: .7; cursor: wait; }
.zip-demo dl { max-width: 480px; margin-bottom: 0; }
@media (max-width: 1180px) {
  .zip-demo { margin-right: 24px; margin-left: 24px; }
}
</style>
