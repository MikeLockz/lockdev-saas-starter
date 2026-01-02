import { N as isDefined, ae as get, R as isObjectLiteral, Z as callAll, e as exclude, r as makeArrayOf } from './misc-811c3842.esm.js';

/** Really, it just returns the value you pass */
const getSelf = state => state;
/** Make an object where the keys will have a self getter as value */
const makeSelfGetters = keys => Object.fromEntries(keys.map(key => [key, getSelf]));

/** Get 1st/only key of object */
const firstKey = obj => Object.keys(obj)[0];

/** Get 1st/only prop of object */
const firstProp = obj => obj[firstKey(obj)];

/** Make getter on obj[key] */
const prop = key => item => item[key];

/** Pick given properties in object */
function pick(obj, paths) {
  const result = {};
  Object.keys(obj).forEach(key => {
    if (!paths.includes(key)) return;
    // @ts-expect-error
    result[key] = obj[key];
  });
  return result;
}
/** Creates an object composed of the picked object properties that satisfies the condition for each value */
function pickBy(obj, paths, fn) {
  const result = {};
  Object.keys(obj).forEach(key => {
    if (!paths.includes(key)) return;
    // @ts-expect-error
    if (!fn(key, obj[key])) return;
    // @ts-expect-error
    result[key] = obj[key];
  });
  return result;
}

/** Only pick given properties that are defined in object */
const pickDefined = (obj, paths) => pickBy(obj, paths, (_key, value) => isDefined(value));

/** Omit given properties from object */
function omit(object, keys) {
  const result = {};
  Object.keys(object).forEach(key => {
    if (keys.includes(key)) return;
    result[key] = object[key];
  });
  return result;
}
/** Format object values using a given method */
const format = (obj, method = getSelf) => Object.keys(obj).reduce((acc, key) => ({
  ...acc,
  [key]: method(obj[key], key)
}), {});

/** Remove undefined properties in object */
const removeUndefineds = obj => Object.keys(obj).reduce((acc, key) => ({
  ...acc,
  ...(isDefined(obj[key]) && {
    [key]: obj[key]
  })
}), {});

/**
 * Returns true if a value differs between a & b, only check for the first level (shallow)
 * @see https://github.com/preactjs/preact-compat/blob/7c5de00e7c85e2ffd011bf3af02899b63f699d3a/src/index.js#L349
 */
function hasShallowDiff(a, b) {
  for (let i in a) if (!(i in b)) return true;
  for (let i in b) if (a[i] !== b[i]) return true;
  return false;
}

/** Returns keys that are both in a & b */
function getCommonKeys(abc, xyz) {
  const keys = [];
  for (let i in abc) {
    if (i in xyz) {
      keys.push(i);
    }
  }
  return keys;
}

/** Returns true if a value differs between a & b in their common properties */
function hasShallowDiffInCommonKeys(abc, xyz) {
  const commonKeys = getCommonKeys(abc, xyz);
  return hasShallowDiff(pick(abc, commonKeys), pick(xyz, commonKeys));
}

/** Map an object to another using given schema, can use a dot delimited path for mapping to nested properties */
const mapper = (schema, obj) => format(Object.entries(schema).reduce((acc, [toKey, fromKey]) => ({
  ...acc,
  [toKey]: get(obj, fromKey)
}), {}));

/** Reverse an object from its schema */
const reverse = schema => Object.entries(schema).reduce((acc, [fromKey, toKey]) => ({
  ...acc,
  [toKey]: fromKey
}), {});

/** Make an instance of given class auto-filled with record values */
const makeInstance = (instance, record) => {
  const item = new instance();
  const entries = Object.entries(record);
  entries.forEach(([key, value]) => item[key] = value);
  return item;
};

/** Polyfill Object.fromEntries */
function fromEntries(iterable) {
  return [...iterable].reduce((obj, [key, val]) => {
    obj[key] = val;
    return obj;
  }, {});
}

/** Sort object keys alphabetically */
const sortObjectKeys = obj => Object.keys(obj).sort().reduce((acc, key) => (acc[key] = obj[key], acc), {});

/** Sort object keys using a reference order array, sort keys not in reference order in lasts positions */
const sortObjKeysFromArray = (obj, orderedKeys) => {
  const entries = Object.entries(obj);
  const sortedEntries = entries.filter(([key]) => orderedKeys.includes(key)).sort(([a], [b]) => orderedKeys.indexOf(a) - orderedKeys.indexOf(b)).concat(entries.filter(([key]) => !orderedKeys.includes(key)));
  return Object.fromEntries(sortedEntries);
};

/**
 * Hashes the value into a stable hash.
 * @see Adapted from https://github.com/tannerlinsley/react-query/blob/e42cbc32dfcd9add24cadd06135e42af1dbbc8ad/src/core/utils.ts
 */
function hash(value) {
  return JSON.stringify(value, (_, val) => isObjectLiteral(val) ? sortObjectKeys(val) : val);
}
function groupBy(array, keyOrGetter) {
  let kv;
  return array.reduce((r, a) => {
    kv = typeof keyOrGetter === "function" ? keyOrGetter(a) : a[keyOrGetter];
    // @ts-ignore
    r[kv] = [...(r[kv] || []), a];
    return r;
  }, {});
}
function groupIn(array, keyOrGetter) {
  let kv;
  return array.reduce((r, a) => {
    kv = typeof keyOrGetter === "function" ? keyOrGetter(a) : a[keyOrGetter];
    // @ts-ignore
    r[kv] = a;
    return r;
  }, {});
}
const mergeProps = (left, right) => {
  const result = {
    ...left,
    ...right
  };
  for (const key in result) {
    if (typeof left[key] === "function" && typeof right[key] === "function") {
      result[key] = callAll(left[key], right[key]);
    }
  }
  return result;
};

// https://github.dev/statelyai/xstate/blob/144131beda5c00a15fbe0f58a3309eac81d940eb/packages/core/src/utils.ts#L39
function keys(value) {
  return Object.keys(value);
}

const truthyRegex = /^(true|1)$/i;
const falsyRegex = /^(false|0)$/i;

/** Parse 'true' and 1 as true, 'false' and 0 as false */
function parseStringAsBoolean(str) {
  if (truthyRegex.test(str)) {
    return true;
  } else if (falsyRegex.test(str)) {
    return false;
  }
  return null;
}
const snakeToCamel = str => str.replace(/(_\w)/g, group => group[1].toUpperCase());
const kebabToCamel = str => str.replace(/(-\w)/g, group => group[1].toUpperCase());
const camelToSnake = str => str.replace(/[\w]([A-Z])/g, group => group[0] + "_" + group[1]).toLowerCase();
const camelToKebab = str => str.replace(/[\w]([A-Z])/g, group => group[0] + "-" + group[1]).toLowerCase();
const uncapitalize = str => str.charAt(0).toLowerCase() + str.slice(1);
const capitalize = str => str.charAt(0).toUpperCase() + str.slice(1);

/** Limit a number between a [min,max] */
const limit = (nb, [min, max]) => Math.min(Math.max(nb, min), max);
const limitStr = (str, limit, fallback = "--") => str?.length >= limit ? fallback : str || fallback;
const areRectsIntersecting = (a, b) => !(a.y + a.height < b.y || a.y > b.y + b.height || a.x + a.width < b.x || a.x > b.x + b.width);
const getSum = arr => arr.reduce((acc, item) => acc + item, 0);
const getClosestNbIn = (arr, to) => arr.reduce((prev, curr) => Math.abs(curr - to) < Math.abs(prev - to) ? curr : prev);
const forceInt = (value, defaultValue = 1) => value = isNaN(value) ? defaultValue : parseInt(value);
const getPageCount = (itemsCount, pageSize) => Math.ceil(itemsCount / pageSize);
const roundTo = (nb, pow = 2) => Math.round(nb * Math.pow(10, pow)) / Math.pow(10, pow);
const stringify = (data, spacing = 2, returnError = false) => {
  try {
    return JSON.stringify(data, null, spacing);
  } catch (error) {
    return returnError ? error : null;
  }
};
const safeJSONParse = (data, returnError = false) => {
  try {
    return JSON.parse(data);
  } catch (error) {
    return returnError ? error : null;
  }
};
const getTotalPages = (totalElements, pageSize) => totalElements ? Math.ceil(totalElements / pageSize) : 0;
function slugify(text) {
  return text.toString() // Cast to string (optional)
  .normalize("NFKD") // The normalize() using NFKD method returns the Unicode Normalization Form of a given string.
  .toLowerCase() // Convert the string to lowercase letters
  .trim() // Remove whitespace from both sides of a string (optional)
  .replace(/\s+/g, "-") // Replace spaces with -
  .replace(/[^\w\-]+/g, "") // Remove all non-word chars
  .replace(/\-\-+/g, "-"); // Replace multiple - with single -
}

const defaultCharacters = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";
const getRandomString = (length = 10, characters = defaultCharacters) => {
  let result = "";
  var charactersLength = characters.length;
  for (var i = 0; i < length; i++) {
    result += characters.charAt(Math.floor(Math.random() * charactersLength));
  }
  return result;
};
function getRandomFloatIn(minOrMax, maxOptional, decimals) {
  const min = maxOptional === undefined ? 0 : minOrMax;
  const max = maxOptional === undefined ? minOrMax : maxOptional;
  const float = Math.random() * (max - min) + min;
  return decimals ? roundTo(float, decimals) : float;
}
const getRandomIntIn = (minOrMax, maxOptional) => Math.floor(getRandomFloatIn(minOrMax, maxOptional));
const getRandomPercent = (decimals = 2) => roundTo(Math.random() * 100, decimals);

/**
 * Randomly pick N unique element in array while excluding some if needed
 * @see https://stackoverflow.com/questions/19269545/how-to-get-a-number-of-random-elements-from-an-array
 */
function pickMultipleUnique(arr, n, excluded = []) {
  if (n >= arr.length) n = arr.length;
  const pickable = exclude(arr, excluded);
  const result = [];
  let picked;
  while (n--) {
    picked = pickOne(exclude(pickable, result));
    result.push(picked);
  }
  return result;
}

/** Returns a random element in given array */
const pickOne = arr => arr[Math.floor(Math.random() * arr.length)];
/** Returns a random element in given array but not of the excluded */
const pickOneBut = (arr, excluded) => {
  const excludedArr = Array.isArray(excluded) ? excluded : [excluded];
  let current;
  do {
    current = pickOne(arr);
  } while (excludedArr.includes(current));
  return current;
};

/** Like pickOne but for typescript enums */
function pickOneInEnum(anEnum, excluded) {
  return pickOneBut(Object.values(anEnum), excluded);
}

/** Make an array of [min, max] empty elements */
const makeArrayOfRandIn = (x = 5, y) => makeArrayOf(getRandomIntIn(x, y));

export { snakeToCamel as A, kebabToCamel as B, camelToSnake as C, camelToKebab as D, uncapitalize as E, capitalize as F, limit as G, limitStr as H, areRectsIntersecting as I, getSum as J, getClosestNbIn as K, forceInt as L, getPageCount as M, roundTo as N, stringify as O, safeJSONParse as P, getTotalPages as Q, slugify as R, getRandomString as S, getRandomFloatIn as T, getRandomIntIn as U, getRandomPercent as V, pickMultipleUnique as W, pickOne as X, pickOneBut as Y, pickOneInEnum as Z, makeArrayOfRandIn as _, firstProp as a, mapper as b, makeInstance as c, fromEntries as d, sortObjKeysFromArray as e, firstKey as f, getSelf as g, hash as h, groupBy as i, groupIn as j, mergeProps as k, keys as l, makeSelfGetters as m, pick as n, pickBy as o, prop as p, pickDefined as q, reverse as r, sortObjectKeys as s, omit as t, format as u, removeUndefineds as v, hasShallowDiff as w, getCommonKeys as x, hasShallowDiffInCommonKeys as y, parseStringAsBoolean as z };
