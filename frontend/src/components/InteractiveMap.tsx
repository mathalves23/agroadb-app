/**
 * Interactive Map Component
 * 
 * Mapa interativo com propriedades rurais usando Leaflet
 */
import React, { useEffect, useRef, useState } from 'react';
import { MapContainer, TileLayer, Marker, Popup, Polygon, useMap } from 'react-leaflet';
import { LatLngExpression, LatLngBoundsExpression, Icon } from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { motion } from 'framer-motion';
import { useTheme } from '../contexts/ThemeContext';

// Fix para ícones padrão do Leaflet
import icon from 'leaflet/dist/images/marker-icon.png';
import iconShadow from 'leaflet/dist/images/marker-shadow.png';
import iconRetina from 'leaflet/dist/images/marker-icon-2x.png';

const DefaultIcon = new Icon({
  iconUrl: icon,
  iconRetinaUrl: iconRetina,
  shadowUrl: iconShadow,
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41]
});

Icon.Default.prototype = DefaultIcon;

// Tipos
interface Property {
  id: string;
  name: string;
  coordinates: LatLngExpression;
  polygon?: LatLngExpression[];
  area: number;
  owner: string;
  status: 'active' | 'inactive' | 'pending';
  source: 'CAR' | 'INCRA' | 'SIGEF';
}

interface InteractiveMapProps {
  properties: Property[];
  center?: LatLngExpression;
  zoom?: number;
  height?: string;
  onPropertyClick?: (property: Property) => void;
}

export function InteractiveMap({
  properties,
  center = [-15.7801, -47.9292], // Brasília
  zoom = 5,
  height = '600px',
  onPropertyClick
}: InteractiveMapProps) {
  const { actualMode } = useTheme();
  const [selectedProperty, setSelectedProperty] = useState<Property | null>(null);
  const [mapStyle, setMapStyle] = useState<'default' | 'satellite' | 'terrain'>('default');

  // Tile layers
  const tileLayers = {
    default: {
      url: actualMode === 'dark'
        ? 'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png'
        : 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
      attribution: '© OpenStreetMap contributors'
    },
    satellite: {
      url: 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
      attribution: '© Esri'
    },
    terrain: {
      url: 'https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png',
      attribution: '© OpenTopoMap'
    }
  };

  const handlePropertyClick = (property: Property) => {
    setSelectedProperty(property);
    onPropertyClick?.(property);
  };

  // Cores por fonte
  const sourceColors = {
    CAR: '#16a34a',
    INCRA: '#0ea5e9',
    SIGEF: '#8b5cf6'
  };

  return (
    <div className="relative" style={{ height }}>
      {/* Map Controls */}
      <div className="absolute top-4 right-4 z-[1000] space-y-2">
        {/* Style Selector */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-2 space-y-1">
          <button
            onClick={() => setMapStyle('default')}
            className={`w-full px-3 py-2 text-sm rounded ${
              mapStyle === 'default'
                ? 'bg-green-600 text-white'
                : 'bg-gray-100 dark:bg-gray-700 text-gray-900 dark:text-white hover:bg-gray-200 dark:hover:bg-gray-600'
            }`}
          >
            🗺️ Padrão
          </button>
          <button
            onClick={() => setMapStyle('satellite')}
            className={`w-full px-3 py-2 text-sm rounded ${
              mapStyle === 'satellite'
                ? 'bg-green-600 text-white'
                : 'bg-gray-100 dark:bg-gray-700 text-gray-900 dark:text-white hover:bg-gray-200 dark:hover:bg-gray-600'
            }`}
          >
            🛰️ Satélite
          </button>
          <button
            onClick={() => setMapStyle('terrain')}
            className={`w-full px-3 py-2 text-sm rounded ${
              mapStyle === 'terrain'
                ? 'bg-green-600 text-white'
                : 'bg-gray-100 dark:bg-gray-700 text-gray-900 dark:text-white hover:bg-gray-200 dark:hover:bg-gray-600'
            }`}
          >
            🏔️ Terreno
          </button>
        </div>

        {/* Legend */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-3">
          <h4 className="text-xs font-bold mb-2 text-gray-900 dark:text-white">Legenda</h4>
          <div className="space-y-1">
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-full bg-green-600"></div>
              <span className="text-xs text-gray-700 dark:text-gray-300">CAR</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-full bg-blue-600"></div>
              <span className="text-xs text-gray-700 dark:text-gray-300">INCRA</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-full bg-purple-600"></div>
              <span className="text-xs text-gray-700 dark:text-gray-300">SIGEF</span>
            </div>
          </div>
        </div>

        {/* Stats */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-3">
          <div className="text-2xl font-bold text-gray-900 dark:text-white">
            {properties.length}
          </div>
          <div className="text-xs text-gray-600 dark:text-gray-400">
            Propriedades
          </div>
        </div>
      </div>

      {/* Map */}
      <MapContainer
        center={center}
        zoom={zoom}
        style={{ height: '100%', width: '100%', borderRadius: '12px' }}
        scrollWheelZoom={true}
      >
        <TileLayer
          url={tileLayers[mapStyle].url}
          attribution={tileLayers[mapStyle].attribution}
        />

        {/* Property Markers */}
        {properties.map((property) => (
          <React.Fragment key={property.id}>
            {/* Marker */}
            <Marker
              position={property.coordinates}
              eventHandlers={{
                click: () => handlePropertyClick(property)
              }}
            >
              <Popup>
                <div className="p-2 min-w-[200px]">
                  <h3 className="font-bold text-lg mb-2">{property.name}</h3>
                  <div className="space-y-1 text-sm">
                    <p><strong>Proprietário:</strong> {property.owner}</p>
                    <p><strong>Área:</strong> {property.area.toLocaleString()} ha</p>
                    <p><strong>Fonte:</strong> {property.source}</p>
                    <p>
                      <span className={`inline-block px-2 py-1 rounded text-xs ${
                        property.status === 'active' ? 'bg-green-100 text-green-800' :
                        property.status === 'inactive' ? 'bg-gray-100 text-gray-800' :
                        'bg-yellow-100 text-yellow-800'
                      }`}>
                        {property.status === 'active' ? 'Ativo' :
                         property.status === 'inactive' ? 'Inativo' : 'Pendente'}
                      </span>
                    </p>
                  </div>
                  <button
                    onClick={() => handlePropertyClick(property)}
                    className="mt-3 w-full px-3 py-1.5 bg-green-600 hover:bg-green-700 text-white text-sm rounded"
                  >
                    Ver Detalhes
                  </button>
                </div>
              </Popup>
            </Marker>

            {/* Polygon (se disponível) */}
            {property.polygon && (
              <Polygon
                positions={property.polygon}
                pathOptions={{
                  color: sourceColors[property.source],
                  fillColor: sourceColors[property.source],
                  fillOpacity: 0.2,
                  weight: 2
                }}
                eventHandlers={{
                  click: () => handlePropertyClick(property)
                }}
              />
            )}
          </React.Fragment>
        ))}
      </MapContainer>

      {/* Selected Property Panel */}
      {selectedProperty && (
        <motion.div
          initial={{ x: -300 }}
          animate={{ x: 0 }}
          exit={{ x: -300 }}
          className="absolute bottom-4 left-4 z-[1000] bg-white dark:bg-gray-800 rounded-lg shadow-2xl p-4 w-80"
        >
          <div className="flex items-start justify-between mb-3">
            <h3 className="font-bold text-lg text-gray-900 dark:text-white">
              {selectedProperty.name}
            </h3>
            <button
              onClick={() => setSelectedProperty(null)}
              className="text-gray-500 hover:text-gray-700 dark:hover:text-gray-300"
            >
              ✕
            </button>
          </div>
          
          <div className="space-y-2 text-sm">
            <div>
              <span className="text-gray-600 dark:text-gray-400">Proprietário:</span>
              <p className="font-medium text-gray-900 dark:text-white">{selectedProperty.owner}</p>
            </div>
            <div>
              <span className="text-gray-600 dark:text-gray-400">Área:</span>
              <p className="font-medium text-gray-900 dark:text-white">
                {selectedProperty.area.toLocaleString()} hectares
              </p>
            </div>
            <div>
              <span className="text-gray-600 dark:text-gray-400">Fonte:</span>
              <p className="font-medium text-gray-900 dark:text-white">{selectedProperty.source}</p>
            </div>
          </div>

          <button
            className="mt-4 w-full px-4 py-2 bg-green-600 hover:bg-green-700 text-white font-medium rounded-lg"
          >
            📄 Ver Relatório Completo
          </button>
        </motion.div>
      )}
    </div>
  );
}

// Componente auxiliar para ajustar bounds do mapa
function MapBounds({ properties }: { properties: Property[] }) {
  const map = useMap();

  useEffect(() => {
    if (properties.length > 0) {
      const bounds = properties.map(p => p.coordinates);
      map.fitBounds(bounds as unknown as LatLngBoundsExpression, { padding: [50, 50] });
    }
  }, [properties, map]);

  return null;
}

// Exemplo de uso com dados mock
export function InteractiveMapDemo() {
  const mockProperties: Property[] = [
    {
      id: '1',
      name: 'Fazenda Santa Rita',
      coordinates: [-15.7801, -47.9292],
      area: 1250,
      owner: 'João Silva',
      status: 'active',
      source: 'CAR',
      polygon: [
        [-15.7701, -47.9192],
        [-15.7701, -47.9392],
        [-15.7901, -47.9392],
        [-15.7901, -47.9192]
      ]
    },
    {
      id: '2',
      name: 'Sítio Boa Vista',
      coordinates: [-15.8801, -48.0292],
      area: 450,
      owner: 'Maria Santos',
      status: 'active',
      source: 'INCRA'
    },
    // ... mais propriedades
  ];

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
          🗺️ Mapa de Propriedades
        </h2>
        <button className="px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg">
          📊 Exportar Dados
        </button>
      </div>

      <InteractiveMap
        properties={mockProperties}
        onPropertyClick={() => {}}
      />
    </div>
  );
}
