[Coding Aider Plan]

## Overview
This plan addresses the `Unresolved reference 'np'` compile error in `analysis_lib/config_defaults.py`. The core fix, which involves importing the `numpy` library, has already been applied. This plan outlines the problem, the solution implemented, and necessary follow-up verification steps to ensure the stability and correctness of the codebase.

## Problem Description
The file `analysis_lib/config_defaults.py` contained references to `np.deg2rad` and `np.rad2deg` within the `DATA_COLUMN_REGISTRY` for 'rotation' conversions. However, the `numpy` library was not imported, leading to `Unresolved reference 'np'` errors during compilation or execution.

## Goals
- Resolve the `Unresolved reference 'np'` error in `analysis_lib/config_defaults.py`.
- Ensure that all `numpy`-dependent functions within `config_defaults.py` are correctly accessible.
- Verify that the fix does not introduce any regressions or new issues in the analysis workflow.

## Additional Notes and Constraints
The primary fix for this issue (adding `import numpy as np`) has already been implemented. The remaining tasks focus on verification and ensuring the overall health of the application. No new features are being added as part of this plan.

## References
None
