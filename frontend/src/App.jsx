import React, { useEffect, useState } from 'react';
import { Bar } from 'react-chartjs-2';
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend } from 'chart.js';

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend);

export default function App() {
  const [data, setData] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await fetch('http://localhost:8001/api/energy');
        const result = await response.json();
        setData(result);
      } catch (error) {
        console.error("Error connecting to backend:", error);
      }
    };

    fetchData();
    const interval = setInterval(fetchData, 180000); // Update every 3 minutes
    return () => clearInterval(interval);
  }, []);

  if (!data) return <div style={{ padding: '20px', color: 'white' }}>Connecting to server...</div>;

  // Chart configuration template
  const createOptions = (title, showLegend = false) => ({
    responsive: true,
    plugins: {
      legend: { display: showLegend, labels: { color: '#cbd5e1' } },
      title: { display: true, text: title, color: '#f8fafc', font: { size: 16 } },
    },
    scales: {
      y: { ticks: { color: '#94a3b8' }, grid: { color: '#334155' } },
      x: { ticks: { color: '#94a3b8' }, grid: { display: false } }
    }
  });

  // Chart data template
  const createData = (zoneData) => ({
    labels: ['Hydro', 'Wind', 'Nuclear'],
    datasets: [{
      label: 'Megawatts',
      data: [zoneData.hydro, zoneData.wind, zoneData.nuclear],
      backgroundColor: ['#3b82f6', '#10b981', '#f59e0b'],
      borderRadius: 4,
    }]
  });

  return (
    <div style={{ padding: '30px', fontFamily: 'system-ui, sans-serif', maxWidth: '1000px', margin: '0 auto', color: '#f8fafc' }}>
      <h1 style={{ textAlign: 'center', margin: '0 0 10px 0' }}>Grid Monitor ⚡</h1>
      <p style={{ textAlign: 'center', color: '#94a3b8', margin: '0 0 30px 0' }}>
        Last synchronized: {new Date(data.last_updated).toLocaleTimeString()}
      </p>
      
      <div style={{ display: 'grid', gap: '20px', gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))' }}>
        
        {/* Main National Chart (Full width) */}
        <div style={{ gridColumn: '1 / -1', background: '#1e293b', padding: '20px', borderRadius: '12px', border: '1px solid #334155' }}>
          <Bar data={createData(data.zones.National)} options={createOptions('National Generation', true)} />
        </div>

        {/* 4 Regional Zone Charts */}
        {['SE1', 'SE2', 'SE3', 'SE4'].map(zone => (
          <div key={zone} style={{ background: '#1e293b', padding: '20px', borderRadius: '12px', border: '1px solid #334155' }}>
            <Bar data={createData(data.zones[zone])} options={createOptions(`Zone ${zone}`)} />
          </div>
        ))}

      </div>
    </div>
  );
}