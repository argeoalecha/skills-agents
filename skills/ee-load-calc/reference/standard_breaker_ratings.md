# Standard Breaker Ampere Ratings (PEC/NEC-style)

15, 20, 25, 30, 35, 40, 45, 50, 60, 70, 80, 90, 100, 110, 125, 150,
175, 200, 225, 250, 300, 350, 400, 450, 500, 600, 700, 800, 1000,
1200, 1600, 2000 A

Used by `select_breaker()` in pec_calc_lib.py to round up to the
next standard size. Verify against manufacturer catalog for the
specific breaker family/frame being specified (e.g. molded case vs
insulated case) — not all ratings exist in every frame size.
