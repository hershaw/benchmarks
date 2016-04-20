'use strict';

var Dodo = require('dodos').default

var timed = require('./timed').timed
var bin = require('./bin')
var apply_transforms = require('./apply_transforms')

const calculate_stats = timed(function calculate_stats(dodo, transforms, index) {
  dodo = apply_transforms(dodo, transforms)
  dodo = new Dodo(dodo.toArray(), dodo.index)

  const stats = dodo
    .cols(index.filter(f => f.type == 'number').map(f => f.name))
    .stats('min', 'max', 'mean')

  for (const col of index) {
    if (col.type == 'number') {
      const s = stats[col.name]
      stats[col.name] = {
        min: s[0],
        max: s[1],
        mean: s[2],
        hist: bin(dodo.col(col.name).toArray(), 30)
      }
    } else if (col.type == 'category') {
      const uniques = [...dodo.col(col.name).groupBy().count().entries()]
      stats[col.name] = {
        uniques: uniques,
        uniqCount: uniques.length
      }
    }
  }

  return stats
})

module.exports = calculate_stats
