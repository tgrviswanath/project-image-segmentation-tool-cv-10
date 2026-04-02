import React from "react";
import { AppBar, Toolbar, Typography } from "@mui/material";
import LayersIcon from "@mui/icons-material/Layers";

export default function Header() {
  return (
    <AppBar position="static" color="primary">
      <Toolbar>
        <LayersIcon sx={{ mr: 1 }} />
        <Typography variant="h6" fontWeight="bold">Image Segmentation Tool</Typography>
      </Toolbar>
    </AppBar>
  );
}
