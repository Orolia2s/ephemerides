# GPS

## Note on page IDs of LNAV messages

While the ICD mentions pages from 1 to 25, the effectively transmitted ID (`SV (page) ID`) goes from 1 to 63.

<table><thead><tr><th>Transmitted</th><th>Subframe</th><th>Page</th><th>Content</th></tr></thead><tbody><tr><td>1</td><td rowspan="3">5</td><td>1</td><td rowspan="9">Almanacs</td></tr><tr><td>...</td><td>...</td></tr><tr><td>24</td><td>24</td></tr><tr><td>25</td><td rowspan="6">4</td><td>2</td></tr><tr><td>...</td><td>...</td></tr><tr><td>28</td><td>5</td></tr><tr><td>29</td><td>7</td></tr><tr><td>...</td><td>...</td></tr><tr><td>32</td><td>10</td></tr><tr><td></td><td></td><td></td><td></td></tr><tr><td>51</td><td>5</td><td>25</td><td>Almanac reference time, satellites health</td></tr><tr><td>52</td><td rowspan="3">4</td><td>13</td><td>NMCT</td></tr><tr><td>56</td><td>18</td><td>Ionospheric correction</td></tr><tr><td>63</td><td>25</td><td>Anti-spoofing flags</td></tr></tbody></table>