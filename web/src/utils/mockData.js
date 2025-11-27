/**
 * Mock Data Generator for Demo/Client Presentation
 * Generates realistic fake data to showcase the bot interface
 */

// Roulette numbers with their colors
const rouletteNumbers = [
  { num: 0, color: 'green' },
  { num: 1, color: 'red' }, { num: 2, color: 'black' }, { num: 3, color: 'red' },
  { num: 4, color: 'black' }, { num: 5, color: 'red' }, { num: 6, color: 'black' },
  { num: 7, color: 'red' }, { num: 8, color: 'black' }, { num: 9, color: 'red' },
  { num: 10, color: 'black' }, { num: 11, color: 'black' }, { num: 12, color: 'red' },
  { num: 13, color: 'black' }, { num: 14, color: 'red' }, { num: 15, color: 'black' },
  { num: 16, color: 'red' }, { num: 17, color: 'black' }, { num: 18, color: 'red' },
  { num: 19, color: 'red' }, { num: 20, color: 'black' }, { num: 21, color: 'red' },
  { num: 22, color: 'black' }, { num: 23, color: 'red' }, { num: 24, color: 'black' },
  { num: 25, color: 'red' }, { num: 26, color: 'black' }, { num: 27, color: 'red' },
  { num: 28, color: 'black' }, { num: 29, color: 'black' }, { num: 30, color: 'red' },
  { num: 31, color: 'black' }, { num: 32, color: 'red' }, { num: 33, color: 'black' },
  { num: 34, color: 'red' }, { num: 35, color: 'black' }, { num: 36, color: 'red' },
];

const getRandomNumber = () => {
  const random = Math.floor(Math.random() * 37);
  return rouletteNumbers[random];
};

const getRandomBetType = () => {
  const types = ['even', 'odd', 'red', 'black'];
  return types[Math.floor(Math.random() * types.length)];
};

const generateResults = (count = 20) => {
  const results = [];
  let spinNumber = 100;
  
  for (let i = 0; i < count; i++) {
    const { num, color } = getRandomNumber();
    const timestamp = new Date(Date.now() - (count - i) * 30000); // 30 seconds apart
    
    results.push({
      spin_number: spinNumber - (count - i - 1),
      number: num,
      color: color,
      zero: num === 0,
      timestamp: timestamp.toISOString(),
    });
  }
  
  return { results: results.reverse() }; // Latest first
};

const generateBalance = () => {
  const initialBalance = 1000.0;
  const currentBalance = 1247.50;
  const profitLoss = currentBalance - initialBalance;
  const todayProfitLoss = 47.50;
  
  return {
    current_balance: currentBalance,
    initial_balance: initialBalance,
    profit_loss: profitLoss,
    today_profit_loss: todayProfitLoss,
    total_bets: 156,
    wins: 82,
    losses: 74,
  };
};

const generateStatus = () => {
  return {
    running: true,
    status: 'running',
    mode: 'Full Auto Mode',
    last_activity: new Date().toISOString(),
    spin_number: 156,
  };
};

const generateActiveBet = () => {
  return {
    bet_type: 'odd',
    bet_amount: 20.0,
    gale_step: 1,
    placed_at: new Date(Date.now() - 15000).toISOString(), // 15 seconds ago
  };
};

const generateBetHistory = (count = 25) => {
  const bets = [];
  let spinNumber = 130;
  let balance = 1000.0;
  
  const betTypes = ['even', 'odd', 'red', 'black'];
  const results = ['win', 'loss'];
  
  for (let i = 0; i < count; i++) {
    const betType = betTypes[Math.floor(Math.random() * betTypes.length)];
    const result = results[Math.floor(Math.random() * 2)];
    const betAmount = 10.0 * Math.pow(2, Math.floor(Math.random() * 3)); // 10, 20, or 40
    const profitLoss = result === 'win' ? betAmount : -betAmount;
    balance += profitLoss;
    
    const timestamp = new Date(Date.now() - (count - i) * 60000); // 1 minute apart
    
    bets.push({
      spin_number: spinNumber + i,
      bet_type: betType,
      bet_amount: betAmount,
      result: result,
      profit_loss: profitLoss,
      balance_after: balance,
      timestamp: timestamp.toISOString(),
    });
  }
  
  return { bets: bets.reverse() }; // Latest first
};

const generateDailyStats = () => {
  const today = new Date();
  const days = [];
  
  for (let i = 6; i >= 0; i--) {
    const date = new Date(today);
    date.setDate(date.getDate() - i);
    
    const spins = 20 + Math.floor(Math.random() * 30);
    const bets = Math.floor(spins * 0.6);
    const wins = Math.floor(bets * 0.52);
    const losses = bets - wins;
    const profitLoss = (wins - losses) * 5 + (Math.random() * 20 - 10);
    
    days.push({
      date: date.toISOString().split('T')[0],
      spins: spins,
      bets: bets,
      wins: wins,
      losses: losses,
      profit_loss: parseFloat(profitLoss.toFixed(2)),
    });
  }
  
  return { stats: days };
};

const generateStrategyStats = () => {
  return {
    stats: [
      {
        strategy: 'even_odd',
        bets: 156,
        wins: 82,
        losses: 74,
        win_rate: 52.56,
        profit_loss: 247.50,
      },
    ],
  };
};

const generateGaleStats = () => {
  return {
    stats: [
      { gale_step: 0, occurrences: 45, wins: 25, losses: 20, profit_loss: 125.0 },
      { gale_step: 1, occurrences: 20, wins: 12, losses: 8, profit_loss: 80.0 },
      { gale_step: 2, occurrences: 8, wins: 5, losses: 3, profit_loss: 40.0 },
      { gale_step: 3, occurrences: 3, wins: 2, losses: 1, profit_loss: 10.0 },
    ],
  };
};

const generateConfig = () => {
  return {
    config: {
      strategy: {
        type: 'even_odd',
        base_bet: 10.0,
        max_gales: 5,
        multiplier: 2.0,
        streak_length: 5,
        zero_policy: 'count_as_loss',
        keepalive_stake: 1.0,
        bet_color_pattern: 'opposite',
        zero_handling: {
          reset_on_zero: true,
        },
      },
      risk: {
        initial_balance: 1000.0,
        stop_loss: 500.0,
        guarantee_fund_percentage: 20,
      },
      session: {
        maintenance_bet_interval: 1800,
        min_bet_amount: 1.0,
      },
      detection: {
        screen_region: [953, 511, 57, 55],
        winning_templates_dir: 'winning-number_templates/',
        winning_template_threshold: 0.65,
        ocr_confidence_threshold: 0.9,
      },
    },
  };
};

const generatePresets = () => {
  return [
    {
      name: 'Conservative',
      slug: 'conservative',
      created_at: new Date(Date.now() - 86400000).toISOString(),
    },
    {
      name: 'Aggressive',
      slug: 'aggressive',
      created_at: new Date(Date.now() - 172800000).toISOString(),
    },
    {
      name: 'Balanced',
      slug: 'balanced',
      created_at: new Date(Date.now() - 259200000).toISOString(),
    },
  ];
};

// Check if demo mode is enabled (via URL parameter or localStorage)
export const isDemoMode = () => {
  if (typeof window === 'undefined') return false;
  
  const urlParams = new URLSearchParams(window.location.search);
  const demoParam = urlParams.get('demo');
  const localStorageDemo = localStorage.getItem('demoMode');
  
  return demoParam === 'true' || localStorageDemo === 'true';
};

// Export all mock data generators
export const mockData = {
  status: generateStatus,
  balance: generateBalance,
  results: generateResults,
  activeBet: generateActiveBet,
  betHistory: generateBetHistory,
  dailyStats: generateDailyStats,
  strategyStats: generateStrategyStats,
  galeStats: generateGaleStats,
  config: generateConfig,
  presets: generatePresets,
};

// Auto-update mock data periodically (for demo)
let updateInterval = null;

export const startMockUpdates = (callback) => {
  if (updateInterval) {
    clearInterval(updateInterval);
  }
  
  // Update results every 5 seconds
  updateInterval = setInterval(() => {
    if (callback) {
      const newResult = generateResults(1);
      callback('new_result', {
        spin_data: newResult.results[0],
      });
    }
  }, 5000);
};

export const stopMockUpdates = () => {
  if (updateInterval) {
    clearInterval(updateInterval);
    updateInterval = null;
  }
};

