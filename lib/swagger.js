import swaggerJSDoc from 'swagger-jsdoc';

const swaggerDefinition = {
  openapi: '3.0.0',
  info: {
    title: 'EmergentTrader API',
    version: '1.0.0',
    description: 'AI-Powered Trading Signal Platform API - Generate, track, and analyze trading signals with Shariah compliance filtering',
    contact: {
      name: 'EmergentTrader Support',
      email: 'support@emergenttrader.com',
    },
    license: {
      name: 'MIT',
      url: 'https://opensource.org/licenses/MIT',
    },
  },
  servers: [
    {
      url: 'http://localhost:3000/api',
      description: 'Development server',
    },
    {
      url: 'https://emergenttrader.com/api',
      description: 'Production server',
    },
  ],
  components: {
    schemas: {
      Stock: {
        type: 'object',
        properties: {
          symbol: {
            type: 'string',
            description: 'Stock symbol (e.g., RELIANCE.NS)',
            example: 'RELIANCE.NS'
          },
          name: {
            type: 'string',
            description: 'Company name',
            example: 'Reliance Industries Limited'
          },
          sector: {
            type: 'string',
            description: 'Industry sector',
            example: 'Oil & Gas'
          },
          market_cap: {
            type: 'number',
            description: 'Market capitalization in crores',
            example: 1500000
          },
          current_price: {
            type: 'number',
            description: 'Current stock price',
            example: 2450.50
          },
          shariah_compliant: {
            type: 'boolean',
            description: 'Whether the stock is Shariah compliant',
            example: true
          },
          last_updated: {
            type: 'string',
            format: 'date-time',
            description: 'Last update timestamp',
            example: '2025-07-26T13:00:00Z'
          }
        }
      },
      TradingSignal: {
        type: 'object',
        properties: {
          signal_id: {
            type: 'string',
            description: 'Unique signal identifier',
            example: '123e4567-e89b-12d3-a456-426614174000'
          },
          symbol: {
            type: 'string',
            description: 'Stock symbol',
            example: 'RELIANCE.NS'
          },
          signal_type: {
            type: 'string',
            enum: ['BUY', 'SELL', 'HOLD'],
            description: 'Type of trading signal',
            example: 'BUY'
          },
          strategy: {
            type: 'string',
            description: 'Strategy used to generate signal',
            example: 'momentum'
          },
          confidence: {
            type: 'number',
            minimum: 0,
            maximum: 1,
            description: 'Signal confidence score (0-1)',
            example: 0.85
          },
          entry_price: {
            type: 'number',
            description: 'Recommended entry price',
            example: 2450.50
          },
          target_price: {
            type: 'number',
            description: 'Target price',
            example: 2650.00
          },
          stop_loss: {
            type: 'number',
            description: 'Stop loss price',
            example: 2300.00
          },
          generated_at: {
            type: 'string',
            format: 'date-time',
            description: 'Signal generation timestamp',
            example: '2025-07-26T13:00:00Z'
          },
          status: {
            type: 'string',
            enum: ['ACTIVE', 'EXECUTED', 'EXPIRED', 'CANCELLED'],
            description: 'Signal status',
            example: 'ACTIVE'
          },
          shariah_compliant: {
            type: 'boolean',
            description: 'Whether the stock is Shariah compliant',
            example: true
          }
        }
      },
      BacktestResult: {
        type: 'object',
        properties: {
          strategy: {
            type: 'string',
            description: 'Strategy name',
            example: 'momentum'
          },
          start_date: {
            type: 'string',
            format: 'date',
            description: 'Backtest start date',
            example: '2020-01-01'
          },
          end_date: {
            type: 'string',
            format: 'date',
            description: 'Backtest end date',
            example: '2024-12-31'
          },
          total_return: {
            type: 'number',
            description: 'Total return percentage',
            example: 45.67
          },
          annualized_return: {
            type: 'number',
            description: 'Annualized return percentage',
            example: 12.34
          },
          sharpe_ratio: {
            type: 'number',
            description: 'Sharpe ratio',
            example: 1.25
          },
          max_drawdown: {
            type: 'number',
            description: 'Maximum drawdown percentage',
            example: -15.67
          },
          win_rate: {
            type: 'number',
            description: 'Win rate percentage',
            example: 65.5
          },
          total_trades: {
            type: 'integer',
            description: 'Total number of trades',
            example: 150
          }
        }
      },
      PerformanceSummary: {
        type: 'object',
        properties: {
          total_signals: {
            type: 'integer',
            description: 'Total signals generated',
            example: 250
          },
          active_signals: {
            type: 'integer',
            description: 'Currently active signals',
            example: 15
          },
          win_rate: {
            type: 'number',
            description: 'Overall win rate percentage',
            example: 68.5
          },
          avg_return: {
            type: 'number',
            description: 'Average return per signal',
            example: 5.67
          },
          best_performing_stock: {
            type: 'string',
            description: 'Best performing stock symbol',
            example: 'RELIANCE.NS'
          },
          worst_performing_stock: {
            type: 'string',
            description: 'Worst performing stock symbol',
            example: 'IDEA.NS'
          }
        }
      },
      ApiResponse: {
        type: 'object',
        properties: {
          success: {
            type: 'boolean',
            description: 'Whether the request was successful',
            example: true
          },
          data: {
            type: 'object',
            description: 'Response data'
          },
          error: {
            type: 'string',
            description: 'Error message if request failed',
            example: 'Invalid parameters provided'
          },
          timestamp: {
            type: 'string',
            format: 'date-time',
            description: 'Response timestamp',
            example: '2025-07-26T13:00:00Z'
          }
        }
      },
      Error: {
        type: 'object',
        properties: {
          success: {
            type: 'boolean',
            example: false
          },
          error: {
            type: 'string',
            description: 'Error message',
            example: 'Resource not found'
          },
          code: {
            type: 'string',
            description: 'Error code',
            example: 'NOT_FOUND'
          },
          timestamp: {
            type: 'string',
            format: 'date-time',
            example: '2025-07-26T13:00:00Z'
          }
        }
      }
    },
    responses: {
      Success: {
        description: 'Successful response',
        content: {
          'application/json': {
            schema: {
              $ref: '#/components/schemas/ApiResponse'
            }
          }
        }
      },
      BadRequest: {
        description: 'Bad request',
        content: {
          'application/json': {
            schema: {
              $ref: '#/components/schemas/Error'
            }
          }
        }
      },
      NotFound: {
        description: 'Resource not found',
        content: {
          'application/json': {
            schema: {
              $ref: '#/components/schemas/Error'
            }
          }
        }
      },
      InternalServerError: {
        description: 'Internal server error',
        content: {
          'application/json': {
            schema: {
              $ref: '#/components/schemas/Error'
            }
          }
        }
      }
    }
  },
  tags: [
    {
      name: 'API Status',
      description: 'API health and status endpoints'
    },
    {
      name: 'Stocks',
      description: 'Stock data management and retrieval'
    },
    {
      name: 'Signals',
      description: 'Trading signal generation and tracking'
    },
    {
      name: 'Backtest',
      description: 'Strategy backtesting and analysis'
    },
    {
      name: 'Performance',
      description: 'Performance metrics and analytics'
    }
  ]
};

const options = {
  swaggerDefinition,
  apis: ['./app/api/**/*.js', './lib/swagger-docs.js'], // Path to the API files
};

const swaggerSpec = swaggerJSDoc(options);

export default swaggerSpec;
