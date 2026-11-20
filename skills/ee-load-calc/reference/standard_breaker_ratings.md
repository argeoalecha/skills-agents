# Standard Breaker Ampere Ratings (PEC/NEC-style)

15, 20, 25, 30, 35, 40, 45, 50, 60, 70, 80, 90, 100, 110, 125, 150,
175, 200, 225, 250, 300, 350, 400, 450, 500, 600, 700, 800, 1000,
1200, 1600, 2000, 2500, 3000, 4000, 5000, 6000 A

Matches NEC Table 240.6(A) (the PEC 2017 counterpart article must be
confirmed against the physical code book). Fuse-only ratings (1, 3, 6,
10, 601 A) are excluded because `select_breaker()` sizes breakers.

Used by `select_breaker()` in pec_calc_lib.py to round up to the
next standard size. Verify against manufacturer catalog for the
specific breaker family/frame being specified (e.g. molded case vs
insulated case) — not all ratings exist in every frame size.
