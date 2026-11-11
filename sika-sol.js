const sikaPanel = document.getElementById('sika-options');
const sikaShape = document.getElementById('sika-shape');
const sikaWidth = document.getElementById('sika-width');
const sikaLength = document.getElementById('sika-length');
const sikaWidthLabel = document.getElementById('sika-width-label');
const sikaDownload = document.getElementById('sika-download');
const sikaAr = document.getElementById('sika-ar');
let sikaUrl;

function makeFloorScene(width, length) {
  const x = width / 2;
  const z = length / 2;
  return `#usda 1.0
(
    defaultPrim = "SikaSolBleu"
    metersPerUnit = 1
    upAxis = "Y"
)
def Xform "SikaSolBleu" {
    def Material "Epoxy" {
        token outputs:surface.connect = </SikaSolBleu/Epoxy/Surface.outputs:surface>
        def Shader "Surface" {
            uniform token info:id = "UsdPreviewSurface"
            color3f inputs:diffuseColor = (0.006, 0.25, 0.56)
            float inputs:metallic = 0
            float inputs:roughness = 0.14
            float inputs:clearcoat = 1
            float inputs:clearcoatRoughness = 0.10
            float inputs:ior = 1.5
            token outputs:surface
        }
    }
    def Mesh "Sol" (
        prepend apiSchemas = ["MaterialBindingAPI"]
    ) {
        uniform bool doubleSided = true
        uniform token subdivisionScheme = "none"
        int[] faceVertexCounts = [4]
        int[] faceVertexIndices = [0, 1, 2, 3]
        point3f[] points = [(-${x}, 0, -${z}), (-${x}, 0, ${z}), (${x}, 0, ${z}), (${x}, 0, -${z})]
        float3[] extent = [(-${x}, 0, -${z}), (${x}, 0, ${z})]
        rel material:binding = </SikaSolBleu/Epoxy>
    }
}
`;
}

// USDZ stores ZIP entries without compression and aligns file data to 64 bytes.
function packFloorUsdz(scene) {
  const encoder = new TextEncoder();
  const name = encoder.encode('sika-sol-bleu.usda');
  const data = encoder.encode(scene);
  let crc = 0xffffffff;
  for (const byte of data) {
    crc ^= byte;
    for (let bit = 0; bit < 8; bit++) {
      crc = (crc >>> 1) ^ (crc & 1 ? 0xedb88320 : 0);
    }
  }
  crc = (crc ^ 0xffffffff) >>> 0;

  const localEnd = 30 + name.length;
  const padding = (64 - (localEnd + 4) % 64) % 64;
  const dataOffset = localEnd + 4 + padding;
  const centralOffset = dataOffset + data.length;
  const centralSize = 46 + name.length;
  const endOffset = centralOffset + centralSize;
  const bytes = new Uint8Array(endOffset + 22);
  const view = new DataView(bytes.buffer);
  const u16 = (offset, value) => view.setUint16(offset, value, true);
  const u32 = (offset, value) => view.setUint32(offset, value, true);

  u32(0, 0x04034b50);
  u16(4, 20);
  u16(12, 33);
  u32(14, crc);
  u32(18, data.length);
  u32(22, data.length);
  u16(26, name.length);
  u16(28, 4 + padding);
  bytes.set(name, 30);
  u16(localEnd, 0x1986);
  u16(localEnd + 2, padding);
  bytes.set(data, dataOffset);

  u32(centralOffset, 0x02014b50);
  u16(centralOffset + 4, 20);
  u16(centralOffset + 6, 20);
  u16(centralOffset + 14, 33);
  u32(centralOffset + 16, crc);
  u32(centralOffset + 20, data.length);
  u32(centralOffset + 24, data.length);
  u16(centralOffset + 28, name.length);
  bytes.set(name, centralOffset + 46);

  u32(endOffset, 0x06054b50);
  u16(endOffset + 8, 1);
  u16(endOffset + 10, 1);
  u32(endOffset + 12, centralSize);
  u32(endOffset + 16, centralOffset);
  return bytes;
}

function readMetres(field) {
  const raw = field.value.trim();
  if (!/^(?:\d+(?:[.,]\d+)?|[.,]\d+)$/.test(raw)) return NaN;
  return Number(raw.replace(',', '.'));
}

function updateSikaFloor() {
  const square = sikaShape.value === 'square';
  sikaLength.parentElement.hidden = square;
  sikaWidthLabel.textContent = square ? 'Côté (m)' : 'Largeur (m)';
  const width = readMetres(sikaWidth);
  const length = square ? width : readMetres(sikaLength);
  const valid = [width, length].every(value => Number.isFinite(value) && value > 0 && value <= 100);

  if (sikaUrl) URL.revokeObjectURL(sikaUrl);
  sikaUrl = undefined;
  sikaAr.hidden = !valid;
  sikaDownload.hidden = !valid;
  document.getElementById('sika-error').hidden = valid;
  if (!valid) {
    sikaAr.removeAttribute('href');
    sikaDownload.removeAttribute('href');
    return;
  }

  const bytes = packFloorUsdz(makeFloorScene(width, length));
  sikaUrl = URL.createObjectURL(new Blob([bytes], {type: 'model/vnd.usdz+zip'}));
  sikaAr.href = sikaUrl + '#allowsContentScaling=0';
  sikaDownload.href = sikaUrl;
  sikaDownload.download = `sika-sol-bleu-${width}x${length}m.usdz`;
  const format = new Intl.NumberFormat('fr-CH', {maximumFractionDigits: 6});
  document.getElementById('sika-size').textContent = `${format.format(width)} × ${format.format(length)} m`;
}

sikaShape.addEventListener('change', updateSikaFloor);
sikaWidth.addEventListener('input', updateSikaFloor);
sikaLength.addEventListener('input', updateSikaFloor);
