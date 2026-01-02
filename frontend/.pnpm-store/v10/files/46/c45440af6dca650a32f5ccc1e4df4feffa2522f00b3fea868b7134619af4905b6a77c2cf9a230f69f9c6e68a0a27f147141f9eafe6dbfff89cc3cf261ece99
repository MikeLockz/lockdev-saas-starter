import * as React from 'react';

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
  const Context = React.createContext(options.initialValue);
  Context.displayName = name;
  function useContext() {
    const context = React.useContext(Context);
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

export { createContextWithHook };
