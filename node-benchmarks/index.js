'use strict';

var sampleSize = require('lodash/fp/sampleSize')
var Dodo = require('dodos').default

var parse = require('./csv-parser').parse
var apply_index = require('./apply_index')
var get_cols = require('./get_cols')
var calculate_stats = require('./calculate_stats')
var saveTimes = require('./timed').saveTimes

// get process arguments
const argv = process.argv.slice(2)
const filepath = argv[0]
const transform_set = argv[1]
const action = argv[2]
const iters = +argv[3]
if (!transform_set || ['small', 'medium', 'large'].indexOf(transform_set) == -1)
  throw new Error('unrecognised transform_set: ' + transform_set)

console.log('\n\nstarting node-' + argv.slice(0, -1).join('-') + '\n\n')

var index = require('../index.json')

require('child_process')
  .execSync('nohup pidstat -r -p ' + process.pid + ' > profile/`hostname`-node-' + argv.slice(0, -1).join('-') + '.mem &')

if (action == 'apply_index') {

  parse(__dirname + '/../data/' + filepath + '.csv', ',')
    .then(result => {
      apply_index(new Dodo(result.data, result.columns), index)
      saveTimes('node', filepath, transform_set, action)
    })
    .catch(console.log.bind(console))

} else if (action == 'get_cols') {

  const transforms = require('../transforms.json')
  const dodo = new Dodo(require('./typed.json'), index.map(f => f.name))

  let i = -1
  while (++i < iters) {
    get_cols(dodo, transforms[transform_set], sampleSize(5, index))
  }

  saveTimes('node', filepath, transform_set, action)

} else if (action == 'calculate_stats') {

  const transforms = require('../transforms.json')
  const dodo = new Dodo(require('./typed.json'), index.map(f => f.name))

  let i = -1
  while (++i < iters) {
    calculate_stats(dodo, transforms[transform_set], sampleSize(5, index))
  }

  saveTimes('node', filepath, transform_set, action)

}
