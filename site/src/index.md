---
layout: base.njk
title: Home
description: Data analysis of non-traffic police calls near four Berkeley motel and hotel conversions to interim and supportive housing.
---

<section class="hero">
  <h1>Berkeley Interim Housing: Police Call Analysis</h1>
  <p class="lead">
    Non-traffic police calls are heavily concentrated near four Berkeley motel and hotel properties converted to interim and supportive housing.
    This site presents an evidence-based analysis using public Berkeley Police data.
  </p>
  <p class="scope-note">
    Results show association and timing patterns only. They do not establish causation.
  </p>
</section>

<section class="hero-chart">
  <div id="chart-hero" class="chart-container" aria-label="Share of non-traffic calls within 100m of each study site">
    <p class="chart-loading">Loading chart…</p>
  </div>
  <p class="chart-note">
    Share of all non-traffic calls within the combined study area that fall within 100 m of each site.
    <a href="/findings/">View full findings →</a>
  </p>
</section>

<section class="site-cards">
  <h2>Sites Studied</h2>
  <p>
    Four motel and hotel properties converted to housing, shelter, or reentry programs.
    The three University Avenue sites form a tight geographic cluster and are analyzed together.
    The San Pablo site is geographically distinct and is analyzed separately.
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
      <a href="/site-profiles/1620-san-pablo/">
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
    <li>What share of non-traffic calls in the study area occur within 100 m of each site?</li>
    <li>Did that concentration increase after site openings?</li>
    <li>Did the University core cluster diverge from comparable Berkeley commercial areas?</li>
    <li>Did the San Pablo node show different patterns from the University cluster?</li>
    <li>Did adjacent blocks show spillover beyond the immediate site area?</li>
  </ul>
  <p><a href="/findings/" class="btn">View Findings</a></p>
</section>

<section class="about-data">
  <h2>Data and Methods</h2>
  <p>
    Analysis uses Berkeley's public calls-for-service data, geocoded from block addresses using the U.S. Census batch geocoder.
    We focused on non-traffic calls — disturbances, welfare checks, theft, and similar public-safety calls.
  </p>
  <p>
    The three University Avenue sites are clustered closely enough that broad neighborhood buffers overlap substantially.
    They are treated as a shared cluster environment with each opening date as a sequential intervention event.
    The San Pablo site is geographically separate and analyzed independently.
  </p>
  <p>
    <a href="/methodology/">Read the full methodology</a> &middot;
    <a href="/data-sources/">Download the data</a>
  </p>
</section>

<script src="/assets/js/chart-hero.js" type="module"></script>
