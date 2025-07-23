import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

const SectorBreakdownChart = ({ data }) => {
  if (!data || data.length === 0) {
    return <div>No sector data available</div>;
  }

  // Transform data for the chart
  const chartData = data.map(sector => ({
    name: sector.sector_name,
    incidents: sector.incident_count,
    critical: sector.critical_count
  }));

  return (
    <ResponsiveContainer width="100%" height={300}>
      <BarChart data={chartData}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis 
          dataKey="name"
          angle={-45}
          textAnchor="end"
          height={100}
        />
        <YAxis />
        <Tooltip />
        <Bar dataKey="incidents" fill="#8884d8" name="Total Incidents" />
        <Bar dataKey="critical" fill="#ff7300" name="Critical Incidents" />
      </BarChart>
    </ResponsiveContainer>
  );
};

export default SectorBreakdownChart;