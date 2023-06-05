# GPS

## Note on page IDs of LNAV messages

While the ICD mentions pages from 1 to 25, the effectively transmitted ID (`SV (page) ID`) goes from 1 to 63.

<table class="tg">
<thead>
  <tr>
    <th class="tg-0lax">Transmitted</th>
    <th class="tg-0lax">Subframe</th>
    <th class="tg-0lax">Page</th>
    <th class="tg-0lax">Content</th>
  </tr>
</thead>
<tbody>
  <tr>
    <td class="tg-0lax">1</td>
    <td class="tg-cly1" rowspan="3">5</td>
    <td class="tg-0lax">1</td>
    <td class="tg-cly1" rowspan="9">Almanacs</td>
  </tr>
  <tr>
    <td class="tg-0lax">...</td>
    <td class="tg-0lax">...</td>
  </tr>
  <tr>
    <td class="tg-0lax">24</td>
    <td class="tg-0lax">24</td>
  </tr>
  <tr>
    <td class="tg-0lax">25</td>
    <td class="tg-cly1" rowspan="6">4</td>
    <td class="tg-0lax">2</td>
  </tr>
  <tr>
    <td class="tg-0lax">...</td>
    <td class="tg-0lax">...</td>
  </tr>
  <tr>
    <td class="tg-0lax">28</td>
    <td class="tg-0lax">5</td>
  </tr>
  <tr>
    <td class="tg-0lax">29</td>
    <td class="tg-0lax">7</td>
  </tr>
  <tr>
    <td class="tg-0lax">...</td>
    <td class="tg-0lax">...</td>
  </tr>
  <tr>
    <td class="tg-0lax">32</td>
    <td class="tg-0lax">10</td>
  </tr>
  <tr>
    <td class="tg-0lax"></td>
    <td class="tg-0lax"></td>
    <td class="tg-0lax"></td>
    <td class="tg-0lax"></td>
  </tr>
  <tr>
    <td class="tg-0lax">51</td>
    <td class="tg-0lax">5</td>
    <td class="tg-0lax">25</td>
    <td class="tg-0lax">Almanac reference time, satellites health</td>
  </tr>
  <tr>
    <td class="tg-0lax">52</td>
    <td class="tg-cly1" rowspan="3">4</td>
    <td class="tg-0lax">13</td>
    <td class="tg-0lax">NMCT</td>
  </tr>
  <tr>
    <td class="tg-0lax">56</td>
    <td class="tg-0lax">18</td>
    <td class="tg-0lax">Ionospheric correction</td>
  </tr>
  <tr>
    <td class="tg-0lax">63</td>
    <td class="tg-0lax">25</td>
    <td class="tg-0lax">Anti-spoofing flags</td>
  </tr>
</tbody>
</table>