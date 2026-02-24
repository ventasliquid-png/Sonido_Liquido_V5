<template>
  <div class="remito-preview-container animate-in">
    <div class="remito-paper shadow-2xl">
      <!-- Watermark for preview -->
      <div class="watermark">VISTA PREVIA</div>

      <!-- Header Section -->
      <div class="header-grid">
        <div class="date-field">
          <span class="label">FECHA:</span>
          <span class="value">{{ today }}</span>
        </div>
        
        <div class="client-info">
          <div class="row">
            <span class="label">SEÑOR(ES):</span>
            <span class="value-bold uppercase">{{ cliente?.razon_social }}</span>
          </div>
          <div class="row grid-2">
            <div>
              <span class="label">CUIT:</span>
              <span class="value font-mono">{{ cliente?.cuit }}</span>
            </div>
            <div>
              <span class="label">IVA:</span>
              <span class="value">{{ cliente?.condicion_iva || 'Resp. Inscripto' }}</span>
            </div>
          </div>
          <div class="row">
            <span class="label">DOMICILIO:</span>
            <span class="value-small uppercase">{{ cliente?.direccion }}</span>
          </div>
        </div>
      </div>

      <!-- Table Section -->
      <div class="items-container">
        <table class="items-table">
          <thead>
            <tr>
              <th class="w-10">CANT.</th>
              <th class="w-10">UNID.</th>
              <th class="w-15">CÓDIGO</th>
              <th>DESCRIPCIÓN</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(item, idx) in items" :key="idx">
              <td class="text-right">{{ item.cantidad }}</td>
              <td class="text-center">UN</td>
              <td>{{ item.codigo || 'S/N' }}</td>
              <td class="uppercase">{{ item.descripcion }}</td>
            </tr>
            <!-- Fill empty lines to maintain height -->
            <tr v-for="i in Math.max(0, 10 - (items?.length || 0))" :key="'empty-'+i">
               <td>&nbsp;</td>
               <td>&nbsp;</td>
               <td>&nbsp;</td>
               <td>&nbsp;</td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Footer Section (ARCA) -->
      <div class="footer-arca">
        <div class="qr-placeholder">
          <i class="fas fa-qrcode"></i>
          <span class="text-[8px]">QR FISCAL</span>
        </div>
        <div class="cae-info">
          <div class="cae-row">
            <span class="cae-label">CAE Nº:</span>
            <span class="cae-value">{{ factura?.cae }}</span>
          </div>
          <div class="cae-row">
            <span class="cae-label">Vto. CAE:</span>
            <span class="cae-value">{{ factura?.vto_cae }}</span>
          </div>
          <p class="legalese">Documento de Transporte amparado por Factura Electrónica vinculada.</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';

const props = defineProps({
  cliente: Object,
  factura: Object,
  items: Array
});

const today = computed(() => {
  return new Date().toLocaleDateString('es-AR');
});
</script>

<style scoped>
.remito-preview-container {
  display: flex;
  justify-content: center;
  padding: 1rem;
  background: #1e293b;
  border-radius: 1rem;
  overflow: hidden;
}

.remito-paper {
  width: 100%;
  max-width: 500px; /* Scale down for UI but keep aspect ratio */
  aspect-ratio: 1 / 1.414; /* A4 aspect ratio */
  background: white;
  color: #1e293b;
  position: relative;
  padding: 40px 30px;
  font-family: 'Courier New', Courier, monospace;
  border: 1px solid #cbd5e1;
}

.watermark {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%) rotate(-45deg);
  font-size: 4rem;
  font-weight: bold;
  color: rgba(226, 232, 240, 0.4);
  pointer-events: none;
  z-index: 10;
}

.header-grid {
  margin-top: 60px; /* Space for letterhead in physical remito */
}

.date-field {
  text-align: right;
  margin-bottom: 30px;
}

.label {
  font-weight: bold;
  font-size: 10px;
  color: #64748b;
  margin-right: 5px;
}

.value {
  font-size: 12px;
  color: #1e293b;
}

.value-bold {
  font-size: 14px;
  font-weight: bold;
  color: #1e293b;
}

.value-small {
  font-size: 10px;
  color: #334155;
}

.row {
  margin-bottom: 8px;
  border-bottom: 1px dotted #e2e8f0;
  padding-bottom: 2px;
}

.grid-2 {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}

.items-container {
  margin-top: 40px;
  min-height: 250px;
}

.items-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 11px;
}

.items-table th {
  text-align: left;
  border-bottom: 2px solid #1e293b;
  padding: 5px;
  font-size: 9px;
  color: #64748b;
}

.items-table td {
  padding: 6px 5px;
  border-bottom: 1px solid #f1f5f9;
}

.text-right { text-align: right; }
.text-center { text-align: center; }
.w-10 { width: 10%; }
.w-15 { width: 15%; }

.footer-arca {
  position: absolute;
  bottom: 40px;
  left: 30px;
  right: 30px;
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  border-top: 2px solid #1e293b;
  padding-top: 15px;
}

.qr-placeholder {
  width: 60px;
  height: 60px;
  border: 1px solid #e2e8f0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #64748b;
}

.cae-info {
  text-align: right;
}

.cae-row {
  margin-bottom: 2px;
}

.cae-label {
  font-size: 9px;
  font-weight: bold;
  margin-right: 5px;
}

.cae-value {
  font-size: 11px;
  font-family: 'Courier New', Courier, monospace;
}

.legalese {
  font-size: 7px;
  font-style: italic;
  color: #94a3b8;
  margin-top: 8px;
}

.uppercase { text-transform: uppercase; }

.animate-in {
  animation: slideUp 0.4s ease-out;
}

@keyframes slideUp {
  from { transform: translateY(20px); opacity: 0; }
  to { transform: translateY(0); opacity: 1; }
}
</style>
