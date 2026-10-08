<script setup>
import HotelDiscovery from './HotelDiscovery.vue'
import LegacyApp from './LegacyApp.vue'
import HotelChat from './HotelChat.vue'
const legacy = window.location.pathname === '/sample-stays'
</script>

<template>
  <LegacyApp v-if="legacy" />
  <template v-else>
    <HotelDiscovery />
    <HotelChat />
  </template>
</template>
