/**
 * @swagger
 * /:
 *   get:
 *     tags: [API Status]
 *     summary: Get API status and information
 *     description: Returns basic information about the EmergentTrader API
 *     responses:
 *       200:
 *         description: API status information
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 success:
 *                   type: boolean
 *                   example: true
 *                 message:
 *                   type: string
 *                   example: "EmergentTrader API v1.0 - Your AI-Powered Trading Signal Platform"
 *                 version:
 *                   type: string
 *                   example: "1.0.0"
 *                 timestamp:
 *                   type: string
 *                   format: date-time
 */

/**
 * @swagger
 * /stocks/all:
 *   get:
 *     tags: [Stocks]
 *     summary: Get all NSE stocks
 *     description: Retrieve all available NSE stocks in the trading universe
 *     responses:
 *       200:
 *         description: List of all NSE stocks
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 success:
 *                   type: boolean
 *                   example: true
 *                 data:
 *                   type: object
 *                   properties:
 *                     stocks:
 *                       type: array
 *                       items:
 *                         $ref: '#/components/schemas/Stock'
 *                     count:
 *                       type: integer
 *                       example: 53
 *       500:
 *         $ref: '#/components/responses/InternalServerError'
 */

/**
 * @swagger
 * /stocks/refresh:
 *   post:
 *     tags: [Stocks]
 *     summary: Refresh stock data
 *     description: Refresh stock data for specified symbols or all Shariah-compliant stocks
 *     requestBody:
 *       required: false
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             properties:
 *               symbols:
 *                 type: array
 *                 items:
 *                   type: string
 *                 description: Array of stock symbols to refresh (optional)
 *                 example: ["RELIANCE.NS", "TCS.NS"]
 *               force:
 *                 type: boolean
 *                 description: Force refresh even if data is recent
 *                 example: false
 *     responses:
 *       200:
 *         description: Stock data refresh results
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 success:
 *                   type: boolean
 *                   example: true
 *                 data:
 *                   type: object
 *                   properties:
 *                     refreshed:
 *                       type: integer
 *                       example: 3
 *                     failed:
 *                       type: integer
 *                       example: 0
 *                     symbols:
 *                       type: array
 *                       items:
 *                         type: string
 *                       example: ["RELIANCE.NS", "TCS.NS", "INFY.NS"]
 *       400:
 *         $ref: '#/components/responses/BadRequest'
 *       500:
 *         $ref: '#/components/responses/InternalServerError'
 */

/**
 * @swagger
 * /stocks/shariah:
 *   get:
 *     tags: [Stocks]
 *     summary: Get Shariah-compliant stocks
 *     description: Retrieve all stocks that are Shariah-compliant for Islamic trading
 *     responses:
 *       200:
 *         description: List of Shariah-compliant stocks
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 success:
 *                   type: boolean
 *                   example: true
 *                 data:
 *                   type: object
 *                   properties:
 *                     stocks:
 *                       type: array
 *                       items:
 *                         $ref: '#/components/schemas/Stock'
 *                     count:
 *                       type: integer
 *                       example: 2
 *       500:
 *         $ref: '#/components/responses/InternalServerError'
 */

/**
 * @swagger
 * /signals/generate:
 *   post:
 *     tags: [Signals]
 *     summary: Generate trading signals
 *     description: Generate new trading signals using specified strategy
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             required:
 *               - strategy
 *             properties:
 *               strategy:
 *                 type: string
 *                 enum: [momentum, mean_reversion, breakout]
 *                 description: Trading strategy to use
 *                 example: "momentum"
 *               symbols:
 *                 type: array
 *                 items:
 *                   type: string
 *                 description: Specific symbols to generate signals for (optional)
 *                 example: ["RELIANCE.NS", "TCS.NS"]
 *               shariah_only:
 *                 type: boolean
 *                 description: Generate signals only for Shariah-compliant stocks
 *                 example: true
 *               min_confidence:
 *                 type: number
 *                 minimum: 0
 *                 maximum: 1
 *                 description: Minimum confidence threshold for signals
 *                 example: 0.6
 *     responses:
 *       200:
 *         description: Generated trading signals
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 success:
 *                   type: boolean
 *                   example: true
 *                 data:
 *                   type: object
 *                   properties:
 *                     signals:
 *                       type: array
 *                       items:
 *                         $ref: '#/components/schemas/TradingSignal'
 *                     count:
 *                       type: integer
 *                       example: 5
 *                     strategy:
 *                       type: string
 *                       example: "momentum"
 *       400:
 *         $ref: '#/components/responses/BadRequest'
 *       500:
 *         $ref: '#/components/responses/InternalServerError'
 */

/**
 * @swagger
 * /signals/track:
 *   post:
 *     tags: [Signals]
 *     summary: Track signal performance
 *     description: Track the performance of specific trading signals
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             required:
 *               - signal_ids
 *             properties:
 *               signal_ids:
 *                 type: array
 *                 items:
 *                   type: string
 *                 description: Array of signal IDs to track
 *                 example: ["123e4567-e89b-12d3-a456-426614174000"]
 *               update_prices:
 *                 type: boolean
 *                 description: Whether to update current prices
 *                 example: true
 *     responses:
 *       200:
 *         description: Signal tracking results
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 success:
 *                   type: boolean
 *                   example: true
 *                 data:
 *                   type: object
 *                   properties:
 *                     tracked:
 *                       type: integer
 *                       example: 1
 *                     results:
 *                       type: array
 *                       items:
 *                         type: object
 *                         properties:
 *                           signal_id:
 *                             type: string
 *                           current_return:
 *                             type: number
 *                           status:
 *                             type: string
 *       400:
 *         $ref: '#/components/responses/BadRequest'
 *       500:
 *         $ref: '#/components/responses/InternalServerError'
 */

/**
 * @swagger
 * /signals/today:
 *   get:
 *     tags: [Signals]
 *     summary: Get today's signals
 *     description: Retrieve all trading signals generated today
 *     parameters:
 *       - in: query
 *         name: strategy
 *         schema:
 *           type: string
 *         description: Filter by strategy
 *       - in: query
 *         name: signal_type
 *         schema:
 *           type: string
 *           enum: [BUY, SELL, HOLD]
 *         description: Filter by signal type
 *       - in: query
 *         name: shariah_only
 *         schema:
 *           type: boolean
 *         description: Show only Shariah-compliant signals
 *     responses:
 *       200:
 *         description: Today's trading signals
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 success:
 *                   type: boolean
 *                   example: true
 *                 data:
 *                   type: object
 *                   properties:
 *                     signals:
 *                       type: array
 *                       items:
 *                         $ref: '#/components/schemas/TradingSignal'
 *                     count:
 *                       type: integer
 *                       example: 8
 *       500:
 *         $ref: '#/components/responses/InternalServerError'
 */

/**
 * @swagger
 * /signals/open:
 *   get:
 *     tags: [Signals]
 *     summary: Get active signals
 *     description: Retrieve all currently active trading signals
 *     parameters:
 *       - in: query
 *         name: strategy
 *         schema:
 *           type: string
 *         description: Filter by strategy
 *       - in: query
 *         name: min_confidence
 *         schema:
 *           type: number
 *           minimum: 0
 *           maximum: 1
 *         description: Minimum confidence threshold
 *     responses:
 *       200:
 *         description: Active trading signals
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 success:
 *                   type: boolean
 *                   example: true
 *                 data:
 *                   type: object
 *                   properties:
 *                     signals:
 *                       type: array
 *                       items:
 *                         $ref: '#/components/schemas/TradingSignal'
 *                     count:
 *                       type: integer
 *                       example: 12
 *       500:
 *         $ref: '#/components/responses/InternalServerError'
 */

/**
 * @swagger
 * /backtest:
 *   post:
 *     tags: [Backtest]
 *     summary: Run strategy backtest
 *     description: Execute a backtest for a specific trading strategy
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             required:
 *               - strategy
 *             properties:
 *               strategy:
 *                 type: string
 *                 enum: [momentum, mean_reversion, breakout]
 *                 description: Strategy to backtest
 *                 example: "momentum"
 *               start_date:
 *                 type: string
 *                 format: date
 *                 description: Backtest start date
 *                 example: "2020-01-01"
 *               end_date:
 *                 type: string
 *                 format: date
 *                 description: Backtest end date
 *                 example: "2024-12-31"
 *               symbols:
 *                 type: array
 *                 items:
 *                   type: string
 *                 description: Specific symbols to backtest (optional)
 *               initial_capital:
 *                 type: number
 *                 description: Initial capital for backtest
 *                 example: 100000
 *               shariah_only:
 *                 type: boolean
 *                 description: Backtest only Shariah-compliant stocks
 *                 example: true
 *     responses:
 *       200:
 *         description: Backtest results
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 success:
 *                   type: boolean
 *                   example: true
 *                 data:
 *                   $ref: '#/components/schemas/BacktestResult'
 *       400:
 *         $ref: '#/components/responses/BadRequest'
 *       500:
 *         $ref: '#/components/responses/InternalServerError'
 */

/**
 * @swagger
 * /performance/summary:
 *   get:
 *     tags: [Performance]
 *     summary: Get performance summary
 *     description: Retrieve overall performance metrics and analytics
 *     parameters:
 *       - in: query
 *         name: period
 *         schema:
 *           type: string
 *           enum: [1d, 7d, 30d, 90d, 1y, all]
 *         description: Time period for performance analysis
 *         example: "30d"
 *       - in: query
 *         name: strategy
 *         schema:
 *           type: string
 *         description: Filter by strategy
 *     responses:
 *       200:
 *         description: Performance summary
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 success:
 *                   type: boolean
 *                   example: true
 *                 data:
 *                   $ref: '#/components/schemas/PerformanceSummary'
 *       500:
 *         $ref: '#/components/responses/InternalServerError'
 */
