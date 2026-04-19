---
layout: base.njk
title: Home
description: Data analysis of non-traffic police calls along the University Avenue corridor near four interim housing conversions in Berkeley.
---

<section class="hero">
  <h1>Berkeley Interim Housing: Police Call Analysis</h1>
  <p class="lead">
    Did non-traffic police calls increase along the University Avenue corridor as four motel and hotel properties were converted to interim and supportive housing?
    This site presents an evidence-based analysis using public Berkeley Police data.
  </p>
  <p class="scope-note">
    Results show association and timing patterns only. They do not establish causation.
  </p>
</section>

<section class="hero-chart">
  <div id="chart-hero" class="chart-container" aria-label="Monthly non-traffic calls along the University Avenue corridor">
    <p class="chart-loading">Loading chart…</p>
  </div>
  <p class="chart-note">
    Monthly non-traffic police calls within the University Avenue corridor cluster.
    Dashed lines mark each site opening date.
    <a href="/findings/">View full findings →</a>
  </p>
</section>

<section class="site-cards">
  <h2>Sites Studied</h2>
  <p>
    Four motel and hotel properties converted to housing, shelter, or reentry programs.
    Because the sites are clustered along the same corridor, the primary analysis treats them as a shared corridor environment
    rather than four separate neighborhood experiments.
  </p>
  <ul class="card-list">
    <li class="card">
      <a href="/site-profiles/1461-university/">
        <strong>1461 University Ave</strong>
        <span class="card-type">Interim housing / shelter</span>
        <span class="card-date">Opened July 2021</span>
      </a>
    </li>
    <li class="card">
      <a href="/site-profiles/1619-university/">
        <strong>1619 University Ave</strong>
        <span class="card-type">Reentry / supportive housing</span>
        <span class="card-date">Opened July 2023</span>
      </a>
    </li>
    <li class="card">
      <a href="/site-profiles/1761-university/">
        <strong>1761 University Ave</strong>
        <span class="card-type">Interim housing</span>
        <span class="card-date">Opened February 2026</span>
      </a>
    </li>
    <li class="card">
      <a href="/site-profiles/golden-bear/">
        <strong>1620 San Pablo Ave</strong>
        <span class="card-type">Permanent supportive housing (Golden Bear Inn)</span>
        <span class="card-date">Opened January 2023</span>
      </a>
    </li>
  </ul>
</section>

<section class="key-questions">
  <h2>Key Questions</h2>
  <ul>
    <li>Did corridor non-traffic calls rise after successive site openings?</li>
    <li>Did the corridor diverge from comparable Berkeley commercial areas?</li>
    <li>Were effects cumulative as more sites opened, or nonlinear?</li>
    <li>Did individual site blocks show localized changes near their opening dates?</li>
  </ul>
  <p><a href="/findings/" class="btn">View Findings</a></p>
</section>

<section class="about-data">
  <h2>Data and Methods</h2>
  <p>
    Analysis uses Berkeley's public calls-for-service data. We focused on non-traffic calls —
    disturbances, welfare checks, theft, and similar public-safety calls.
    Because the four sites sit close together along University Avenue, broad neighborhood buffers
    overlap substantially. To avoid double-counting, the primary analysis treats the corridor as
    a single treatment area and each opening date as a sequential intervention event.
  </p>
  <p>
    <a href="/methodology/">Read the full methodology</a> &middot;
    <a href="/data-sources/">Download the data</a>
  </p>
</section>

<script src="/assets/js/chart-hero.js" type="module"></script>
