// main.js - v20.3 SMART MODE - Africa/Lagos - NO EMOJI VERSION
require('dotenv').config();
const express = require('express');
const axios = require('axios');
const cron = require('node-cron');
const moment = require('moment-timezone');
const fs = require('fs');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 3000;
const API_KEY = process.env.FOOTBALL_API_KEY;
const TIMEZONE = 'Africa/Lagos';

process.env.TZ = TIMEZONE;
console.log('Timezone set: ' + TIMEZONE + ' - Current: ' + moment().tz(TIMEZONE).format('YYYY-MM-DD HH:mm:ss'));

function smartPick(homeTeam, awayTeam, stats) {
  const markets = [];
  const homeGoals = stats.homeAvgGoals || 1.8;
  const awayGoals = stats.awayAvgGoals || 1.2;
  const homeConcede = stats.homeConcede || 1.0;
  const awayConcede = stats.awayConcede || 1.5;

  const teamOverProb = homeGoals > 1.8? 0.88 : 0.75;
  markets.push({
    market: homeTeam + ' Team Over 1.5',
    odd: homeGoals > 2.2? 1.32 : 1.55,
    w: Math.round(teamOverProb * 100),
    rating: teamOverProb > 0.85? 9.9 : 9.5
  });

  const winOverProb = homeGoals > 1.5 && awayConcede > 1.3? 0.83 : 0.70;
  markets.push({
    market: homeTeam + ' Win + Over 1.5',
    odd: 1.35,
    w: Math.round(winOverProb * 100),
    rating: winOverProb > 0.80? 9.8 : 9.3
  });

  const over25Prob = (homeGoals + awayGoals) > 2.5? 0.82 : 0.71;
  markets.push({
    market: 'Over 2.5',
    odd: (homeGoals + awayGoals) > 2.8? 1.45 : 2.05,
    w: Math.round(over25Prob * 100),
    rating: over25Prob > 0.80? 9.7 : 9.3
  });

  const bttsProb = homeConcede > 1.0 && awayGoals > 0.9? 0.75 : 0.60;
  markets.push({
    market: 'BTTS Yes',
    odd: 1.70,
    w: Math.round(bttsProb * 100),
    rating: bttsProb > 0.72? 9.5 : 9.0
  });

  markets.sort((a, b) => (b.w - a.w) || (b.odd - a.odd));
  return markets[0];
}

async function updateFixtures(dateStr, forceSmart) {
  const date = dateStr || moment().tz(TIMEZONE).format('YYYY-MM-DD');
  console.log('[' + moment().tz(TIMEZONE).format() + '] Updating fixtures for ' + date);

  try {
    if (!fs.existsSync('./data')) fs.mkdirSync('./data');

    // Mock data if API fails - replace with real API later
    const mockFixtures = [
      { id: 1, homeTeam: { name: 'Bayern Munich' }, awayTeam: { name: 'Bodo Glimt' }, utcDate: new Date().toISOString() },
      { id: 2, homeTeam: { name: 'Man Utd' }, awayTeam: { name: 'Sabah' }, utcDate: new Date().toISOString() },
      { id: 3, homeTeam: { name: 'PSV' }, awayTeam: { name: 'Shakhtar Donetsk' }, utcDate: new Date().toISOString() },
      { id: 4, homeTeam: { name: 'Fenerbahce' }, awayTeam: { name: 'AS Roma' }, utcDate: new Date().toISOString() },
      { id: 5, homeTeam: { name: 'Como' }, awayTeam: { name: 'RB Leipzig' }, utcDate: new Date().toISOString() },
      { id: 6, homeTeam: { name: 'Slavia Praha' }, awayTeam: { name: 'Lens' }, utcDate: new Date().toISOString() }
    ];

    let matches = mockFixtures;
    try {
      const res = await axios.get('https://api.football-data.org/v4/matches?date=' + date + '&competitions=CL', {
        headers: { 'X-Auth-Token': API_KEY }
      });
      if (res.data.matches && res.data.matches.length > 0) matches = res.data.matches.slice(0, 6);
    } catch (apiErr) {
      console.log('API failed, using mock: ' + apiErr.message);
    }

    const fixtures = matches.map(m => {
      const stats = {
        homeAvgGoals: Math.random() * 1 + 1.5,
        awayAvgGoals: Math.random() * 0.8 + 0.8,
        homeConcede: Math.random() * 0.5 + 0.8,
        awayConcede: Math.random() * 0.8 + 1.0
      };
      const best = smartPick(m.homeTeam.name, m.awayTeam.name, stats);
      return {
        id: m.id,
        home: m.homeTeam.name,
        away: m.awayTeam.name,
        time: moment(m.utcDate).tz(TIMEZONE).format('HH:mm WAT'),
        bestPick: best,
        date: date
      };
    });

    fs.writeFileSync('./data/fixtures-' + date + '.json', JSON.stringify(fixtures, null, 2));
    const top3 = fixtures.sort((a,b) => b.bestPick.w - a.bestPick.w).slice(0, 3);
    const ticketOdd = top3.reduce((acc, f) => acc * f.bestPick.odd, 1).toFixed(2);
    const avgW = Math.round(top3.reduce((acc, f) => acc + f.bestPick.w, 0) / 3);
    console.log('Updated ' + fixtures.length + ' fixtures with SMART picks');
    console.log('Best ticket: ' + ticketOdd + ' W' + avgW);
    return fixtures;
  } catch (e) {
    console.error('Update failed: ' + e.message);
    throw e;
  }
}

cron.schedule('0 6 * * *', async () => {
  console.log('CRON triggered at ' + moment().tz(TIMEZONE).format('YYYY-MM-DD HH:mm:ss WAT'));
  await updateFixtures();
}, { timezone: TIMEZONE });

app.get('/', async (req, res) => {
  const today = moment().tz(TIMEZONE).format('YYYY-MM-DD');
  let fixtures = [];
  try {
    const data = fs.readFileSync('./data/fixtures-' + today + '.json', 'utf8');
    fixtures = JSON.parse(data);
  } catch (err) {
    fixtures = await updateFixtures(today, true);
  }
  res.json({ version: 'v20.3 SMART', timezone: TIMEZONE, date: today, fixtures: fixtures });
});

app.get('/api/cron/update', async (req, res) => {
  if (req.query.secret!== process.env.CRON_SECRET) return res.status(403).send('Forbidden');
  const date = req.query.date || moment().tz(TIMEZONE).format('YYYY-MM-DD');
  const fixtures = await updateFixtures(date, true);
  res.json({ success: true, fixtures: fixtures });
});

app.listen(PORT, () => {
  console.log('Engine v20.3 SMART running on port ' + PORT);
  console.log('Time: ' + moment().tz(TIMEZONE).format('dddd, MMMM Do YYYY, HH:mm:ss WAT'));
});

module.exports = { updateFixtures, smartPick };
