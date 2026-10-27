// Huna Robo removable controller tray — PARAMETRIC TEMPLATE ONLY
// Units: mm. Required board dimensions intentionally default to 0.
// OpenSCAD will stop with an assertion until real measurements are supplied.
// Do not export this file as a final part before fit checks.

// Required measured dimensions:
board_x = 0;          // PCB width, mm — measure actual board
board_y = 0;          // PCB length, mm — measure actual board
board_z = 0;          // max component height, mm — clearance reference

// Design allowances (confirm based on printer/material and actual connectors):
side_clearance = 2.0;
end_clearance = 4.0;
plate_t = 3.0;
wall_t = 2.4;
wall_h = 8.0;
corner_r = 4.0;

// Mounting-hole pattern is intentionally disabled until measured.
// Set true only after hole coordinates and diameter are verified.
use_board_holes = false;
hole_d = 0;
hole_x = [];          // X coordinates relative to PCB centre
hole_y = [];          // Y coordinates relative to PCB centre

assert(board_x > 0 && board_y > 0 && board_z > 0,
       "Set board_x, board_y and board_z from measured/official dimensions.");
assert(side_clearance >= 0 && end_clearance >= 0);
assert(plate_t >= 2 && wall_t >= 1.6 && wall_h > 0);
assert(!use_board_holes || (hole_d > 0 && len(hole_x) > 0 && len(hole_y) > 0),
       "Board hole pattern enabled but hole dimensions/coordinates are missing.");

tray_x = board_x + 2*side_clearance;
tray_y = board_y + 2*end_clearance;

module rounded_plate(x, y, z, r) {
    hull() {
        for (sx=[-1,1], sy=[-1,1])
            translate([sx*(x/2-r), sy*(y/2-r), 0])
                cylinder(h=z, r=r, $fn=32);
    }
}

difference() {
    union() {
        // Base and perimeter lips; top remains open for board removal.
        rounded_plate(tray_x + 2*wall_t, tray_y + 2*wall_t,
                      plate_t, corner_r);
        translate([-(tray_x/2+wall_t), -(tray_y/2+wall_t), plate_t])
            cube([wall_t, tray_y+2*wall_t, wall_h]);
        translate([(tray_x/2), -(tray_y/2+wall_t), plate_t])
            cube([wall_t, tray_y+2*wall_t, wall_h]);
        translate([-(tray_x/2), -(tray_y/2+wall_t), plate_t])
            cube([tray_x, wall_t, wall_h]);
        translate([-(tray_x/2), (tray_y/2), plate_t])
            cube([tray_x, wall_t, wall_h]);
    }

    // Optional PCB mounting holes. Coordinates must be measured.
    if (use_board_holes)
        for (x=hole_x, y=hole_y)
            translate([x, y, -0.1])
                cylinder(h=plate_t+0.2, d=hole_d, $fn=32);
}

// This template does not include robot-body attachment holes because the
// existing body's interface and available mounting points must be inspected
// before those locations can be safely specified.
