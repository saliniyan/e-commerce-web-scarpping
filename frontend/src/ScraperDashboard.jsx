import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Table, TableHeader, TableRow, TableCell, TableBody } from "@/components/ui/table";

export default function ScraperDashboard() {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(false);
  
  const fetchData = async () => {
    try {
      setLoading(true);
      const response = await fetch("http://localhost:5000/data");
      const result = await response.json();
      setData(result);
    } catch (error) {
      console.error("Error fetching data:", error);
    } finally {
      setLoading(false);
    }
  };

  const startScraping = async () => {
    try {
      setLoading(true);
      await fetch("http://localhost:5000/scrape", { method: "POST" });
      fetchData();
    } catch (error) {
      console.error("Error starting scraping:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-4">Scraper Dashboard</h1>
      <Button onClick={startScraping} disabled={loading}>
        {loading ? "Scraping..." : "Start Scraping"}
      </Button>
      <Card className="mt-6">
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableCell>Source</TableCell>
                <TableCell>Data</TableCell>
                <TableCell>Date</TableCell>
              </TableRow>
            </TableHeader>
            <TableBody>
              {data.map((item, index) => (
                <TableRow key={index}>
                  <TableCell>{item.source}</TableCell>
                  <TableCell>{JSON.stringify(item.data)}</TableCell>
                  <TableCell>{item.scraped_date}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  );
}
1