'use strict';

// returns an iteratee function for use in filter
function dropFunc(dodo, command) {
  var set = new Set(command.payload)
  const i = dodo.index[command.name]
  return row => !set.has(row[i])
}

// returns an iteratee function for use in map
function combineFunc(dodo, command) {
  var repwith = command.payload.sort().join('_')
  var set = new Set(command.payload)
  const i = dodo.index[command.name]
  return row => {
    if (set.has(row[i]))
      row[i] = repwith
    return row
  }
}

function apply_transforms(dodo, transforms) {
  for (const t of transforms) {
    if (t.type == 'drop') {
      dodo = dodo.filter(dropFunc(dodo, t))
    } else if (t.type == 'combine') {
      dodo = dodo.map(combineFunc(dodo, t))
    }
  }
  return dodo
}

module.exports = apply_transforms
