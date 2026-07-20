/**
 * Dashboard Component
 * Main dashboard for EREN web application
 */
"use client";

import { useQuery } from "@tanstack/react-query";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";

interface MetricData {
  date: string;
  devices: number;
  incidents: number;
}

export function Dashboard() {
  const { data: metrics } = useQuery<MetricData[]>({
    queryKey: ["dashboard-metrics"],
    queryFn: async () => {
      const response = await fetch("/api/v1/dashboard/metrics");
      return response.json();
    },
  });

  return (
    <div className="p-6 space-y-6">
      <h1 className="text-3xl font-bold">EREN Dashboard</h1>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardHeader>
            <CardTitle>Active Devices</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-4xl font-bold">247</p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader>
            <CardTitle>Open Incidents</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-4xl font-bold">12</p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader>
            <CardTitle>AI Recommendations</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-4xl font-bold">8</p>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Device Metrics</CardTitle>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={metrics || []}>
              <XAxis dataKey="date" />
              <YAxis />
              <CartesianGrid strokeDasharray="3 3" />
              <Tooltip />
              <Line type="monotone" dataKey="devices" stroke="#8884d8" />
            </LineChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>
    </div>
  );
}

export default Dashboard;
