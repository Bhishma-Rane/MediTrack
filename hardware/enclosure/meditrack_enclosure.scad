// MediTrack Part 1 prototype enclosure.
// Units: millimetres. Open in OpenSCAD and render with F6.
// This is a fit-check model, not a validated medical-device enclosure.

$fn = 48;

// Primary parameters
outer_x = 180;
outer_y = 125;
outer_z = 48;
wall = 3;
corner_r = 10;
lid_t = 3;
insert_x = 150;
insert_y = 88;
insert_depth = 18;
oled_window_x = 42;
oled_window_y = 24;
button_d = 10;

module rounded_box(size, radius) {
    hull() {
        for (x = [radius, size[0] - radius])
            for (y = [radius, size[1] - radius])
                translate([x, y, 0]) cylinder(r=radius, h=size[2]);
    }
}

module base_shell() {
    difference() {
        rounded_box([outer_x, outer_y, outer_z], corner_r);
        translate([wall, wall, wall])
            rounded_box([outer_x-2*wall, outer_y-2*wall, outer_z], corner_r-wall);
        // OLED window in the front wall (front is y=0)
        translate([(outer_x-oled_window_x)/2, -1, outer_z-31])
            cube([oled_window_x, wall+2, oled_window_y]);
        // Recessed button holes
        for (x = [outer_x-55, outer_x-37, outer_x-19])
            translate([x, -1, 13]) rotate([-90,0,0])
                cylinder(d=button_d, h=wall+2);
        // Cable gland and buzzer vent
        translate([outer_x/2, outer_y+1, 12]) rotate([90,0,0])
            cylinder(d=8, h=wall+2);
        for (x = [outer_x/2-12, outer_x/2-4, outer_x/2+4, outer_x/2+12])
            translate([x, outer_y/2, outer_z-2]) cylinder(d=2.5, h=5);
    }
}

module insert_tray() {
    // Separate, removable medication insert; rounded inside corners keep it
    // cleanable and avoid medication-catching pockets.
    difference() {
        rounded_box([insert_x, insert_y, insert_depth], 6);
        translate([wall, wall, wall])
            rounded_box([insert_x-2*wall, insert_y-2*wall, insert_depth], 4);
    }
}

module lid() {
    difference() {
        rounded_box([outer_x, outer_y, lid_t], corner_r);
        // Four captive-screw pilot holes; use inserts appropriate to the print.
        for (p = [[12,12], [outer_x-12,12], [12,outer_y-12], [outer_x-12,outer_y-12]])
            translate([p[0], p[1], -1]) cylinder(d=3.2, h=lid_t+2);
    }
}

// Exploded layout for preview: base, insert, then lid.
translate([0,0,0]) base_shell();
translate([(outer_x-insert_x)/2, (outer_y-insert_y)/2, wall+1]) insert_tray();
translate([0, outer_y+15, outer_z+10]) lid();
