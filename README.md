<h1>spl_widgets <sub><sup> by CTSF</sup></sub></h1>
<span><i>widgets created for the Barnard Speech Perception Laboratory</i></span>

<h2>Changelog </h2>
<h3>[NOTE]: June 2022 - This changelog is now SEVERELY out of date as a result of some lazy POS who declines to update it regularly. But on the plus side, less work for me </h3>
<span><i>Note that not every update will be documented here, only those which make large or important changes.
<br>(Or that I am non-lazy enough to document, because formatting is a drag)</i></span>
<details>
  <summary>
    <i>(Click to expand)</i>
  </summary>
<table name="Changelog">
    <tr name="Headings">
      <th>Version</th>
      <th>Summary of Changes</th>
    </tr>
    <tr name="v0.2.5">
      <td name="version_name" align="center" valign="top">
        <strong><a href="https://pypi.org/project/spl-widgets/0.2.5/"> v0.2.5</a></strong>
      </td>
      <td name="changes">
        <ul>
          <li>Changed README.md formatting to be compatible with PyPi's Markdown renderer and converted it to HTML in its entirety.</li>
        </ul>
      </td>
    </tr>
    <tr name="v0.2.4">
      <td name="version_name" align="center" valign="top">
        <strong><a href="https://pypi.org/project/spl-widgets/0.2.4/">v0.2.4</a></strong>
      </td>
      <td name="changes">
        <ul>
          <li> Added changelog. No previous versions have any such documentation. documentation for this module and its individual widgets will increase with time.</li>
          <li>Fixed a typo in tuner.py's <i>tuneWithData</i> function that caused subprocess.run to return an error while attempting to open outputted tuned file.</li>
          <li>Made changes to stk_swx.py to allow for dynamic detection of the number of active formants present within the user's file.</li>
          <li>Added type-hinting to misc_util.py, tune_freq.py and stk_swx.py for clarity.</li>
          <li>Removed ridiculous over-commenting in tune_freq.py and refactored its main function, no changes to functionality made</li>
        </ul>
      </td>
    </tr> 
</table>
</details>
