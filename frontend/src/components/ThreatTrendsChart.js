import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

const ThreatTrendsChart = ({ data }) => {
  if (!data || data.length === 0) {
    return <div>No trend data available</div>;
  }

  return (
    <ResponsiveContainer width="100%" height={300}>
      <LineChart data={data}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis 
          dataKey="date"
          tickFormatter={(value) => new Date(value).toLocaleDateString()}
        />
        <YAxis />
        <Tooltip 
          labelFormatter={(value) => new Date(value).toLocaleDateString()}
          formatter={(value) => [value, 'Incidents']}
        />
        <Line 
          type="monotone" 
          dataKey="incident_count" 
          stroke="#8884d8" 
          strokeWidth={2}
          dot={{ fill: '#8884d8' }}
        />
      </LineChart>
    </ResponsiveContainer>
  );
};

export default ThreatTrendsChart;