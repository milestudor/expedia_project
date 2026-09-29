<script setup>
import HotelDiscovery from './HotelDiscovery.vue'
import LegacyApp from './LegacyApp.vue'
const legacy = window.location.pathname === '/sample-stays'
</script>

<template>
  <LegacyApp v-if="legacy" />
  <HotelDiscovery v-else />
</template>
