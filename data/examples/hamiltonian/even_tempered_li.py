#!/usr/bin/env python

import numpy as np
from horton import *

# specify the even tempered basis set
alpha_low = 5e-3
alpha_high = 5e2
nbasis = 30
lnratio = (np.log(alpha_high) - np.log(alpha_low))/(nbasis-1)

# build a list of "contractions". These aren't real contractions as every
# contraction only contains one basis function.
bcs = []
for ibasis in xrange(nbasis):
    alpha = alpha_low * np.exp(lnratio * ibasis)
    # arguments of GOBasisContraction:
    #     shell_type, list of exponents, list of contraction coefficients
    bcs.append(GOBasisContraction(0, np.array([alpha]), np.array([1.0])))

# Finish setting up the basis set:
ba = GOBasisAtom(bcs)
obasis = get_gobasis(np.array([[0.0, 0.0, 0.0]]), np.array([3]), default=ba)


# CODE BELOW IS FOR horton-regression-test.py ONLY. IT IS NOT PART OF THE EXAMPLE.
rt_results = {
    'scales': obasis.get_scales()
}
# BEGIN AUTOGENERATED CODE. DO NOT CHANGE MANUALLY.
rt_previous = {
    'scales': np.array([
        0.013401011981382846, 0.018048783700127666, 0.024308506962500243,
        0.032739242741423244, 0.044093946902429959, 0.059386717304072578,
        0.079983363702002319, 0.10772338932847644, 0.14508427842131391,
        0.1954027623550548, 0.26317282583235962, 0.35444706831084288, 0.47737726658062746,
        0.64294241657582896, 0.86592927642596351, 1.1662529838442486, 1.5707356932652521,
        2.1155020842604459, 2.8492056860355119, 3.8373741636728487, 5.168261647165739,
        6.9607307795074735, 9.3748684359572785, 12.626283213000068, 17.005361607360911,
        22.903202670074823, 30.846547380648691, 41.544822312114547, 55.953499094940575,
        75.359428365025664
    ]),
}
