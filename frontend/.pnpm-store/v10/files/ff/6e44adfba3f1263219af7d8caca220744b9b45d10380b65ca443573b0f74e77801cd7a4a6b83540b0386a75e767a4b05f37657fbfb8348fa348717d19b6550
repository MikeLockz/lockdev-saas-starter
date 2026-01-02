'use strict';

Object.defineProperty(exports, '__esModule', { value: true });

var React = require('react');

function _interopNamespace(e) {
    if (e && e.__esModule) return e;
    var n = Object.create(null);
    if (e) {
        Object.keys(e).forEach(function (k) {
            if (k !== 'default') {
                var d = Object.getOwnPropertyDescriptor(e, k);
                Object.defineProperty(n, k, d.get ? d : {
                    enumerable: true,
                    get: function () { return e[k]; }
                });
            }
        });
    }
    n["default"] = e;
    return Object.freeze(n);
}

var React__namespace = /*#__PURE__*/_interopNamespace(React);

/** @see https://antfu.me/posts/destructuring-with-object-or-array */
function createIsomorphicDestructurable(obj, arr) {
  const clone = {
    ...obj
  };
  Object.defineProperty(clone, Symbol.iterator, {
    enumerable: false,
    value() {
      let index = 0;
      return {
        next: () => ({
          value: arr[index++],
          done: index > arr.length
        })
      };
    }
  });
  return clone;
}

// Adapted from https://github.com/chakra-ui/chakra-ui/blob/27eec8de744d05eef5bcbd2de651f3a37370ff2c/packages/react-utils/src/context.ts

function createContextWithHook(nameOrOptions, optionsProp = {
  name: undefined
}) {
  const options = typeof nameOrOptions === "string" ? optionsProp : nameOrOptions;
  const name = typeof nameOrOptions === "string" ? nameOrOptions : options.name;
  const {
    strict = false,
    errorMessage = `useContext: "${name || "context"}" is undefined. Seems you forgot to wrap component within the Provider`
  } = options;
  const Context = React__namespace.createContext(options.initialValue);
  Context.displayName = name;
  function useContext() {
    const context = React__namespace.useContext(Context);
    if (!context && strict) {
      const error = new Error(errorMessage);
      error.name = "ContextError";
      // @ts-ignore
      Error.captureStackTrace?.(error, useContext);
      throw error;
    }
    return context;
  }
  return createIsomorphicDestructurable({
    Consumer: Context.Consumer,
    hook: useContext,
    Context: Context,
    Provider: Context.Provider
  }, [Context.Provider, useContext, Context]);
}

exports.createContextWithHook = createContextWithHook;
