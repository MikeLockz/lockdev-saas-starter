'use strict';

const isDefined = value => value !== undefined && value !== null && (typeof value === "string" ? value.trim() !== "" : true);
const isNotNullish = element => element != null;

/** Returns true if value is a string|number|boolean */
const isPrimitive = value => !["object", "function", "symbol"].includes(typeof value) || value === null;

/** Returns true if typeof value is object && not null */
const isObject = value => value !== null && typeof value === "object";
/** Returns true if value extends basic Object prototype and is not a Date */
const isObjectLiteral = value => isObject(value) && value.constructor.name === "Object";
const isDate = value => isType(value, value instanceof Date);
const isPromise = p => p !== null && typeof p === "object" && typeof p.then === "function";

/** Can be used as type guard  */
const isType = (_value, condition) => condition;
const isClassRegex = /^\s*class\s+/;
const isClass = value => typeof value === "function" && isClassRegex.test(value?.toString?.());
const isServer = () => typeof window === "undefined";
const isBrowser = () => !isServer();

// https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Set
function getSetDifference(setA, setB) {
  const _difference = new Set(setA);
  for (let elem of setB) {
    _difference.delete(elem);
  }
  return _difference;
}
function isSuperset(set, subset) {
  for (let elem of subset) {
    if (!set.has(elem)) {
      return false;
    }
  }
  return true;
}
function getSetUnion(setA, setB) {
  let _union = new Set(setA);
  for (let elem of setB) {
    _union.add(elem);
  }
  return _union;
}
function getSetIntersection(setA, setB) {
  let _intersection = new Set();
  for (let elem of setB) {
    if (setA.has(elem)) {
      _intersection.add(elem);
    }
  }
  return _intersection;
}
function getSymmetricDifference(setA, setB) {
  let _difference = new Set(setA);
  for (let elem of setB) {
    if (_difference.has(elem)) {
      _difference.delete(elem);
    } else {
      _difference.add(elem);
    }
  }
  return _difference;
}

/** Sets a nested property value from a dot-delimited path */

function set(obj, pathOrGetter, valueOrProp, value) {
  if (typeof pathOrGetter === "function") {
    const parent = pathOrGetter(obj);
    if (parent) {
      parent[valueOrProp] = value;
    }
    return;
  }
  if (pathOrGetter.includes(".")) {
    let target = obj;
    const props = pathOrGetter.split(".");
    for (let i = 0, len = props.length; i < len; ++i) {
      if (i + 1 < len) {
        if (target[props[i]] === undefined || target[props[i]] === null) {
          target = target[props[i]] = {};
        } else {
          target = target[props[i]];
        }
      } else {
        target[props[i]] = valueOrProp;
      }
    }
    return;
  }
  obj[pathOrGetter] = value;
}
const makeGetter = path => {
  if (path.includes(".")) {
    return new Function("obj", "return obj." + path);
  }
  return obj => obj[path];
};

/** Get a nested property value from a dot-delimited path. */
function get(obj, path) {
  let target = obj || {};
  const props = path.split(".");
  for (let i = 0, len = props.length; i < len; ++i) {
    target = target[props[i]];
    if (target === undefined || target === null) {
      break;
    }
  }
  return target;
}

/** Remove key at path in an object */
function remove(obj, path) {
  let target = obj;
  const props = path.split(".");
  for (let i = 0, len = props.length; i < len; ++i) {
    if (i < len - 1) {
      target = target[props[i]];
      if (undefined === target) {
        break;
      }
    } else {
      delete target[props[i]];
    }
  }
}
/** Deep merge arrays from left into right, can use unique array values for merged properties */
function deepMerge(inputs, options) {
  const objects = inputs.filter(isObjectLiteral);
  let target = objects.shift();
  if (!target) return null;
  if (!objects.length) return target;
  function deepMergeInner(target, source, options) {
    Object.keys(source).forEach(key => {
      const targetValue = target[key];
      const sourceValue = source[key];
      if (Array.isArray(targetValue) && Array.isArray(sourceValue)) {
        target[key] = options?.withUniqueArrayValues ? Array.from(getSetUnion(new Set(targetValue), new Set(sourceValue))) : targetValue.concat(sourceValue);
      } else if (isObject(targetValue) && isObject(sourceValue)) {
        target[key] = deepMergeInner(Object.assign({}, targetValue), sourceValue, options);
      } else {
        target[key] = sourceValue;
      }
    });
    return target;
  }
  let source;
  while (source = objects.shift()) {
    deepMergeInner(target, source, options);
  }
  return target;
}
// Adapted from https://github.com/IndigoUnited/js-deep-sort-object/blob/master/index.js
const defaultSortFn = (a, b) => a.localeCompare(b);
/** Deeply sort an object's properties using given sort function */
function deepSort(src, comparator = defaultSortFn) {
  function deepSortInner(src, comparator) {
    if (Array.isArray(src)) {
      return src.map(item => deepSort(item, comparator));
    }
    if (isObject(src) && !isDate(src)) {
      const out = {};
      Object.keys(src).sort(comparator).forEach(key => out[key] = deepSort(src[key], comparator));
      return out;
    }
    return src;
  }
  return deepSortInner(src, comparator);
}

/**
 * Return the difference between left in right
 * @example getDiff([1, 2, 3], [1, 4, 5]) -> [2, 3]
 */
const getDiff = (left, right) => Array.from(getSetDifference(new Set(left), new Set(right)));

/**
 * Return the difference between left in right / right in left
 * @example getSymmetricDiff([1, 2, 3], [1, 4, 5]) -> [2, 3, 4, 5]
 */
const getSymmetricDiff = (left, right) => Array.from(getSymmetricDifference(new Set(left), new Set(right)));

/**
 * Return the union between left & right
 * @example getUnion([1, 2, 3], [1, 4, 5]) -> [1, 2, 3, 4, 5]
 */
const getUnion = (left, right) => Array.from(getSetUnion(new Set(left), new Set(right)));

/**
 * Return the intersection between left & right
 * @example getUnion([1, 2, 3], [1, 4, 5]) -> [1]
 */
const getIntersection = (left, right) => Array.from(getSetIntersection(new Set(left), new Set(right)));

/**
 * Checks that all items (right) are in left array
 * @example hasAll([1, 2, 3], [1, 4, 5]) = false
 * @example hasAll([1, 2, 3, 4, 5], [1, 4, 5]) = true
 */
const hasAll = (inArray, items) => isSuperset(new Set(inArray), new Set(items));

/**
 * Return uniques/de-duplicated values in array
 * @example uniques([1, 2, 3, 4, 5].concat([6, 7, 1, 2, 9])) // = [1, 2, 3, 4, 5, 6, 7, 9]
 */
const uniques = arr => Array.from(new Set(arr));

/** Return uniques/de-duplicated values in array of objects using the given propPath as unique identifier */
const uniquesByProp = (arr, propPathOrGetter) => {
  if (typeof propPathOrGetter === "function") {
    return arr.reduce((acc, item) => acc.find(current => propPathOrGetter(current) === propPathOrGetter(item)) ? acc : acc.concat(item), []);
  }
  if (propPathOrGetter.includes(".")) {
    const getter = new Function("obj", "propPath", "return obj." + propPathOrGetter);
    return arr.reduce((acc, item) => acc.find(current => getter(current, propPathOrGetter) === getter(item, propPathOrGetter)) ? acc : acc.concat(item), []);
  }
  return arr.reduce((acc, item) => acc.find(current => current[propPathOrGetter] === item[propPathOrGetter]) ? acc : acc.concat(item), []);
};

/** Exclude items in array */
const exclude = (arr, excluded) => arr.filter(item => !excluded.includes(item));

/** Find an item/index from its value using a property path in the array (can be nested using a dot delimited syntax) */
const findBy = (arr, path, value, index) => {
  const getter = makeGetter(path);
  return arr[index ? "findIndex" : "find"](item => getter(item) === value);
};
function findRight(arr = [], predicate) {
  for (let i = arr.length - 1; i >= 0; i--) {
    if (predicate(arr[i])) {
      return arr[i];
    }
  }
}
const compareBasic = (a, b) => a === b ? 0 : a > b ? 1 : -1;

/** Sort an array of objects by a common prop key (or dot-delimited path) in given direction (asc|desc, defaults to asc) */
function sortBy(arr, key, dir = "asc") {
  let aProp;
  let bProp;
  const clone = [...arr];
  const getter = makeGetter(key);
  clone.sort(function (left, right) {
    aProp = getter(left) || "";
    aProp = aProp.toLowerCase ? aProp.toLowerCase() : aProp;
    bProp = getter(right) || "";
    bProp = bProp.toLowerCase ? bProp.toLowerCase() : bProp;
    if (!aProp && !bProp) return 0;
    if (!aProp) return -1;
    if (!bProp) return 1;
    if (typeof aProp === "string" && typeof bProp === "string") {
      return dir === "asc" ? aProp.localeCompare(bProp) : bProp.localeCompare(aProp);
    }
    if (aProp instanceof Date && bProp instanceof Date) {
      return dir === "asc" ? compareBasic(aProp.getTime(), bProp.getTime()) : compareBasic(bProp.getTime(), aProp.getTime());
    }
    if (aProp === bProp) {
      return 0;
    }
    if (aProp < bProp) {
      return dir === "asc" ? -1 : 1;
    }
    return dir === "asc" ? 1 : -1;
  });
  return clone;
}

/** Compare (to sort) 2 objects by a common prop key (or dot-delimited path) in given direction (asc|desc, defaults to asc) */
function sortCompareFn(left, right, key, dir = "asc") {
  let aProp;
  let bProp;
  const getter = makeGetter(key);
  aProp = getter(left) || "";
  aProp = aProp.toLowerCase ? aProp.toLowerCase() : aProp;
  bProp = getter(right) || "";
  bProp = bProp.toLowerCase ? bProp.toLowerCase() : bProp;
  if (!aProp && !bProp) return 0;
  if (!aProp) return -1;
  if (!bProp) return 1;
  if (typeof aProp === "string" && typeof bProp === "string") {
    return dir === "asc" ? aProp.localeCompare(bProp) : bProp.localeCompare(aProp);
  }
  if (aProp instanceof Date && bProp instanceof Date) {
    return dir === "asc" ? compareBasic(aProp.getTime(), bProp.getTime()) : compareBasic(bProp.getTime(), aProp.getTime());
  }
  if (aProp === bProp) {
    return 0;
  }
  if (aProp < bProp) {
    return dir === "asc" ? -1 : 1;
  }
  return dir === "asc" ? 1 : -1;
}

/** Compare arrays & return true if all members are included (order doesn't matter) */
function isEqualArrays(arr1, arr2) {
  if (arr1.length !== arr2.length) return false;
  let i;
  for (i = arr1.length; i--;) {
    if (!arr2.includes(arr1[i])) return false;
  }
  return true;
}

/** Combine one or more array into the first one while pushing only distinct unique values */
const combineUniqueValues = (arr1 = [], ...arr2) => arr2.reduce((acc, nextArr) => Array.from(new Set(acc.concat(nextArr))), arr1);

/** Combine one or more array of objects into the first one while pushing only distinct unique objects using the given propPath as unique identifier */
const combineUniqueValuesByProps = (arrays, propPath) => arrays.reduce((acc, nextArr) => uniquesByProp(acc.concat(nextArr), propPath), []);

/** Get first item of array */
const first = value => value[0];
/** Get last item of array */
const last = value => value[value.length - 1];

/** Polyfill Array.flatMap */
function flatMap(array, callbackfn) {
  return Array.prototype.concat(...array.map(callbackfn));
}

/** Make an array of {count} empty elements */
const makeArrayOf = count => Array(count).fill(0);

/** Split an array in chunk of given size */
const chunk = (arr, size) => arr.reduce((chunks, el, i) => (i % size ? chunks[chunks.length - 1].push(el) : chunks.push([el])) && chunks, []);

/** Array of picked property */
const pluck = (arr, prop) => arr.map(item => item[prop]);

// https://github.com/chakra-ui/chakra-ui/blob/main/packages/utils/src/array.ts
const prependItem = (array, item) => [item, ...array];
const appendItem = (array, item) => [...array, item];
const updateItem = (array, idPath, update) => {
  const clone = [...array];
  const index = findBy(array, idPath, update[idPath], true);
  clone[index] = update;
  return clone;
};
const removeValue = (array, item) => array.filter(eachItem => eachItem !== item);
const removeValueMutate = (array, item) => array.splice(array.indexOf(item), 1);
const removeItem = (array, idPath, value) => array.filter(eachItem => get(eachItem, idPath) !== value);
const removeItemMutate = (array, idPath, value) => array.splice(findBy(array, idPath, value, true), 1);
const updateAtIndex = (array, index, update) => {
  const clone = [...array];
  clone[index] = update;
  return clone;
};
const removeAtIndex = (array, index) => array.filter((_, idx) => idx !== index);
const removeAtIndexMutate = (array, index) => array.splice(index, 1);
function getPrevItem(array, index, loop = true, step) {
  const prevIndex = getPrevIndex(index, array.length, loop, step);
  return array[prevIndex];
}
function getNextItem(array, index, loop = true, step) {
  const nextIndex = getNextIndex(index, array.length, loop, step);
  return array[nextIndex];
}

/**
 * Get the next index based on the current index and step.
 *
 * @param currentIndex the current index
 * @param length the total length or count of items
 * @param step the number of steps
 * @param loop whether to circle back once `currentIndex` is at the start/end
 */
function getNextIndex(currentIndex, length, loop = true, step = 1) {
  const lastIndex = length - 1;
  if (currentIndex === -1) {
    return step > 0 ? 0 : lastIndex;
  }
  const nextIndex = currentIndex + step;
  if (nextIndex < 0) {
    return loop ? lastIndex : 0;
  }
  if (nextIndex >= length) {
    if (loop) return 0;
    return currentIndex > length ? length : currentIndex;
  }
  return nextIndex;
}

/**
 * Get's the previous index based on the current index.
 * Mostly used for keyboard navigation.
 *
 * @param index - the current index
 * @param length - the length or total length of items in the array
 * @param loop - whether we should circle back to the
 * first/last once `currentIndex` is at the start/end
 */
function getPrevIndex(index, length, loop = true, step = -1) {
  return getNextIndex(index, length, loop, step);
}

/** Sort array of object by given prop using a reference order array, sort items not in reference order in lasts positions */
const sortArrayOfObjectByPropFromArray = (arr, prop, orderedProp) => {
  const getter = makeGetter(prop);
  const sortedEntries = arr.filter(item => orderedProp.includes(getter(item))).sort((a, b) => orderedProp.indexOf(getter(a)) - orderedProp.indexOf(getter(b))).concat(arr.filter(item => !orderedProp.includes(getter(item))));
  return sortedEntries;
};

/** Sort array of object by given prop using a reference order array, sort items not in reference order in lasts positions */
const sortListFromRefArray = (arr, orderedProp) => {
  const sortedEntries = arr.filter(item => orderedProp.includes(item)).sort((a, b) => orderedProp.indexOf(a) - orderedProp.indexOf(b)).concat(arr.filter(item => !orderedProp.includes(item)));
  return sortedEntries;
};
const castAsArray = value => Array.isArray(value) ? value : [value].filter(Boolean);

/** Returns a callback that will call all functions passed with the same arguments */
const callAll = (...fns) => (...args) => fns.forEach(fn => fn?.(...args));

/** Returns a callback that will return true if all functions passed with the same arguments returns true */
const needsAll = (...fns) => (...args) => {
  for (const fn of fns) {
    if (!fn?.(...args)) {
      return false;
    }
  }
  return true;
};
/** Compose left-to-right, most commonly used direction */
const pipe = (...fns) => value => fns.reduce((acc, fn) => fn(acc), value);

/** Compose right-to-left */
const compose = (...fns) => value => fns.reduceRight((acc, fn) => fn(acc), value);

/** Compose right-to-left using async fn */
const composeAsync = (...functions) => item => functions.reduceRight((chain, func) => chain.then(func), Promise.resolve(item));

/** Compose left-to-right, most commonly used direction, using async fn */
const pipeAsync = (...functions) => item => functions.reduce((chain, func) => chain.then(func), Promise.resolve(item));

/** Wait for X ms till resolving promise (with optional callback) */
const wait = (duration, callback) => new Promise(resolve => setTimeout(() => resolve(callback?.()), duration));

/**
 * Gets given's entity all inherited classes.
 * Gives in order from parents to children.
 * For example Post extends ContentModel which extends Unit it will give
 * [Unit, ContentModel, Post]
 *
 * Taken from typeorm/src/metadata-builder/MetadataUtils.ts
 * @see https://github.com/typeorm/typeorm/
 */
function getInheritanceTree(entity) {
  const tree = [entity];
  const getPrototypeOf = object => {
    const proto = Object.getPrototypeOf(object);
    if (proto?.name) {
      tree.push(proto);
      getPrototypeOf(proto);
    }
  };
  getPrototypeOf(entity);
  return tree;
}

// Shorthand
const on = (obj, type, listener, options) => {
  obj.addEventListener(type, listener, options);
  return () => off(obj, type, listener, options);
};
const off = (obj, type, listener, options) => obj.removeEventListener(type, listener, options);
const getQueryParams = () => new URLSearchParams(window.location.search);
const getQueryString = data => new URLSearchParams(data).toString();
const makeCompiledFnWith = (code, context) => new Function(...Object.keys(context), code)(...Object.values(context));

/** @see Adapted from https://github.com/devld/go-drive/blob/6a126a6daa92af871ae5233306a808c81c749e70/web/src/utils/index.ts */
const debounce = (func, wait) => {
  let timeout;
  return function (...params) {
    const later = () => {
      timeout = undefined;
      func.apply(this, params);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
};
/** @see Adapted from https://github.com/devld/go-drive/blob/6a126a6daa92af871ae5233306a808c81c749e70/web/src/utils/index.ts */
function throttle(func, wait, options) {
  let context, args, result;
  let timeout;
  let previous = 0;
  if (!options) options = {};
  const later = function () {
    previous = options?.leading === false ? 0 : Date.now();
    timeout = undefined;
    result = func.apply(context, args);
    if (!timeout) {
      context = null;
      args = null;
    }
  };
  return function (...params) {
    const now = Date.now();
    if (!previous && options?.leading === false) previous = now;
    const remaining = wait - (now - previous);
    args = params;
    if (remaining <= 0 || remaining > wait) {
      if (timeout) {
        clearTimeout(timeout);
        timeout = undefined;
      }
      previous = now;
      result = func.apply(context, args);
      if (!timeout) context = args = null;
    } else if (!timeout && options?.trailing !== false) {
      timeout = setTimeout(later, remaining);
    }
    return result;
  };
}

exports.appendItem = appendItem;
exports.callAll = callAll;
exports.castAsArray = castAsArray;
exports.chunk = chunk;
exports.combineUniqueValues = combineUniqueValues;
exports.combineUniqueValuesByProps = combineUniqueValuesByProps;
exports.compareBasic = compareBasic;
exports.compose = compose;
exports.composeAsync = composeAsync;
exports.debounce = debounce;
exports.deepMerge = deepMerge;
exports.deepSort = deepSort;
exports.exclude = exclude;
exports.findBy = findBy;
exports.findRight = findRight;
exports.first = first;
exports.flatMap = flatMap;
exports.get = get;
exports.getDiff = getDiff;
exports.getInheritanceTree = getInheritanceTree;
exports.getIntersection = getIntersection;
exports.getNextIndex = getNextIndex;
exports.getNextItem = getNextItem;
exports.getPrevIndex = getPrevIndex;
exports.getPrevItem = getPrevItem;
exports.getQueryParams = getQueryParams;
exports.getQueryString = getQueryString;
exports.getSetDifference = getSetDifference;
exports.getSetIntersection = getSetIntersection;
exports.getSetUnion = getSetUnion;
exports.getSymmetricDiff = getSymmetricDiff;
exports.getSymmetricDifference = getSymmetricDifference;
exports.getUnion = getUnion;
exports.hasAll = hasAll;
exports.isBrowser = isBrowser;
exports.isClass = isClass;
exports.isClassRegex = isClassRegex;
exports.isDate = isDate;
exports.isDefined = isDefined;
exports.isEqualArrays = isEqualArrays;
exports.isNotNullish = isNotNullish;
exports.isObject = isObject;
exports.isObjectLiteral = isObjectLiteral;
exports.isPrimitive = isPrimitive;
exports.isPromise = isPromise;
exports.isServer = isServer;
exports.isSuperset = isSuperset;
exports.isType = isType;
exports.last = last;
exports.makeArrayOf = makeArrayOf;
exports.makeCompiledFnWith = makeCompiledFnWith;
exports.makeGetter = makeGetter;
exports.needsAll = needsAll;
exports.off = off;
exports.on = on;
exports.pipe = pipe;
exports.pipeAsync = pipeAsync;
exports.pluck = pluck;
exports.prependItem = prependItem;
exports.remove = remove;
exports.removeAtIndex = removeAtIndex;
exports.removeAtIndexMutate = removeAtIndexMutate;
exports.removeItem = removeItem;
exports.removeItemMutate = removeItemMutate;
exports.removeValue = removeValue;
exports.removeValueMutate = removeValueMutate;
exports.set = set;
exports.sortArrayOfObjectByPropFromArray = sortArrayOfObjectByPropFromArray;
exports.sortBy = sortBy;
exports.sortCompareFn = sortCompareFn;
exports.sortListFromRefArray = sortListFromRefArray;
exports.throttle = throttle;
exports.uniques = uniques;
exports.uniquesByProp = uniquesByProp;
exports.updateAtIndex = updateAtIndex;
exports.updateItem = updateItem;
exports.wait = wait;
