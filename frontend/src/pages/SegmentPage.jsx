import React, { useState, useRef } from "react";
import {
  Box, CircularProgress, Alert, Typography, Paper,
  Chip, Grid, Divider, Table, TableBody, TableCell,
  TableHead, TableRow, LinearProgress, Tabs, Tab,
} from "@mui/material";
import UploadFileIcon from "@mui/icons-material/UploadFile";
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell,
} from "recharts";
import { segmentImage } from "../services/segmentApi";

export default function SegmentPage() {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [imgTab, setImgTab] = useState(0);
  const fileRef = useRef();

  const handleFile = async (file) => {
    if (!file) return;
    setLoading(true); setError(""); setResult(null);
    try {
      const fd = new FormData();
      fd.append("file", file);
      const r = await segmentImage(fd);
      setResult(r.data);
    } catch (e) {
      setError(e.response?.data?.detail || "Segmentation failed.");
    } finally {
      setLoading(false);
    }
  };

  const chartData = result
    ? Object.entries(result.class_summary).map(([label, count]) => ({ label, count }))
    : [];

  return (
    <Box>
      <Paper
        variant="outlined"
        onClick={() => fileRef.current.click()}
        onDrop={(e) => { e.preventDefault(); handleFile(e.dataTransfer.files[0]); }}
        onDragOver={(e) => e.preventDefault()}
        sx={{ p: 3, mb: 2, textAlign: "center", cursor: "pointer", borderStyle: "dashed", "&:hover": { bgcolor: "action.hover" } }}
      >
        <input ref={fileRef} type="file" hidden accept=".jpg,.jpeg,.png,.bmp,.webp"
          onChange={(e) => handleFile(e.target.files[0])} />
        {loading
          ? <Box><CircularProgress size={28} sx={{ mb: 1 }} /><Typography color="text.secondary">Segmenting…</Typography></Box>
          : <Box sx={{ display: "flex", alignItems: "center", justifyContent: "center", gap: 1 }}>
              <UploadFileIcon color="action" />
              <Typography color="text.secondary">Drag & drop or click — JPG / PNG / BMP / WEBP</Typography>
            </Box>
        }
      </Paper>

      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

      {result && (
        <Box>
          <Box sx={{ display: "flex", gap: 1.5, mb: 2, flexWrap: "wrap" }}>
            <Chip label={`${result.segment_count} segment${result.segment_count !== 1 ? "s" : ""}`}
              color={result.segment_count > 0 ? "success" : "default"} />
            <Chip label={result.model} variant="outlined" size="small" />
            <Chip label={`${result.image_width} × ${result.image_height} px`} variant="outlined" size="small" />
          </Box>

          {/* Image tabs: annotated vs mask */}
          <Tabs value={imgTab} onChange={(_, v) => setImgTab(v)} sx={{ mb: 1 }}>
            <Tab label="Segmented" />
            <Tab label="Mask Only" />
          </Tabs>
          <Paper variant="outlined" sx={{ p: 1, mb: 2 }}>
            <img
              src={`data:image/jpeg;base64,${imgTab === 0 ? result.annotated_image : result.mask_image}`}
              alt="result" style={{ width: "100%", borderRadius: 4 }} />
          </Paper>

          {result.segment_count > 0 && (
            <>
              <Divider sx={{ mb: 2 }} />
              <Grid container spacing={2}>
                {/* Class distribution chart */}
                <Grid item xs={12} md={5}>
                  <Typography variant="subtitle2" gutterBottom>Class Distribution</Typography>
                  <ResponsiveContainer width="100%" height={Math.max(120, chartData.length * 40)}>
                    <BarChart data={chartData} layout="vertical"
                      margin={{ top: 0, right: 30, bottom: 0, left: 60 }}>
                      <XAxis type="number" allowDecimals={false} />
                      <YAxis type="category" dataKey="label" tick={{ fontSize: 12 }} width={60} />
                      <Tooltip />
                      <Bar dataKey="count" radius={[0, 4, 4, 0]}>
                        {chartData.map((_, i) => (
                          <Cell key={i} fill={`hsl(${i * 37}, 70%, 50%)`} />
                        ))}
                      </Bar>
                    </BarChart>
                  </ResponsiveContainer>
                </Grid>

                {/* Segments table */}
                <Grid item xs={12} md={7}>
                  <Typography variant="subtitle2" gutterBottom>Segments</Typography>
                  <Paper variant="outlined" sx={{ maxHeight: 300, overflow: "auto" }}>
                    <Table size="small" stickyHeader>
                      <TableHead>
                        <TableRow sx={{ bgcolor: "grey.50" }}>
                          <TableCell>#</TableCell>
                          <TableCell>Color</TableCell>
                          <TableCell>Label</TableCell>
                          <TableCell>Conf</TableCell>
                          <TableCell>Coverage</TableCell>
                        </TableRow>
                      </TableHead>
                      <TableBody>
                        {result.segments.map((s) => (
                          <TableRow key={s.id} hover>
                            <TableCell>{s.id + 1}</TableCell>
                            <TableCell>
                              <Box sx={{
                                width: 20, height: 20, borderRadius: 1,
                                bgcolor: `rgb(${s.color[0]},${s.color[1]},${s.color[2]})`,
                              }} />
                            </TableCell>
                            <TableCell>
                              <Chip label={s.label} size="small" variant="outlined" />
                            </TableCell>
                            <TableCell>{s.confidence}%</TableCell>
                            <TableCell>
                              <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
                                <LinearProgress variant="determinate" value={Math.min(s.coverage_pct * 5, 100)}
                                  sx={{ flex: 1, height: 6, borderRadius: 3 }} />
                                <Typography variant="caption">{s.coverage_pct}%</Typography>
                              </Box>
                            </TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </Paper>
                </Grid>
              </Grid>
            </>
          )}

          {result.segment_count === 0 && (
            <Alert severity="info">No objects segmented. Try a clearer image with distinct objects.</Alert>
          )}
        </Box>
      )}
    </Box>
  );
}
