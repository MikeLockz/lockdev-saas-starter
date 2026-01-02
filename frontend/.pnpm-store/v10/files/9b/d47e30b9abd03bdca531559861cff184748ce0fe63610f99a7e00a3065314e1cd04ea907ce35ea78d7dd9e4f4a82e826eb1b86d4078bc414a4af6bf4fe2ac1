'use strict';

Object.defineProperty(exports, '__esModule', { value: true });

var xstate = require('xstate');
var misc = require('../../dist/misc-a5381864.cjs.prod.js');

const makePoolMachine = params => xstate.createMachine({
  id: "pool",
  initial: "idle",
  tsTypes: {},
  schema: {
    context: {},
    events: {}
  },
  context: {
    concurrency: params.concurrency,
    delayInMs: params.delayInMs,
    runningList: [],
    resolvedList: [],
    rejectedList: []
  },
  states: {
    idle: {
      on: {
        START: [{
          target: "started",
          cond: () => Boolean(params.taskList.length)
        }, {
          target: "done"
        }]
      }
    },
    started: {
      invoke: {
        id: "scheduler",
        src: ctx => (sender, onReceive) => {
          const pool = {
            runningList: [],
            pendingList: params.taskList.map((_, i) => i)
          };
          let isMounted = true;
          const ref = {
            concurrency: ctx.concurrency
          };
          onReceive(e => {
            if (e.type === "UPDATE_CONCURRENCY") {
              ref.concurrency = e.concurrency;
            }
          });
          function invokeTask() {
            const index = pool.pendingList.shift();
            const task = params.taskList[index];
            if (!task || !isMounted) return;
            const promise = task();
            sender({
              type: `task.started`,
              index
            });
            promise.then(result => {
              if (!isMounted) return;
              sender({
                type: `task.resolved`,
                index,
                result
              });
            }).catch(error => {
              if (!isMounted) return;
              sender({
                type: `task.rejected`,
                index,
                error
              });
            }).finally(() => {
              if (!isMounted) return;
              pool.runningList = pool.runningList.filter(i => i !== index);
              onSettled();
            });
            pool.runningList.push(index);
          }
          const onSettled = () => {
            if (!isMounted) return;
            if (!pool.pendingList.length) {
              if (!pool.runningList.length) sender({
                type: "DONE"
              });
              return;
            }
            const emptySlotCount = Math.min(ref.concurrency - pool.runningList.length, pool.pendingList.length);
            if (emptySlotCount <= 0) return;
            if (ctx.delayInMs) {
              setTimeout(() => {
                misc.makeArrayOf(emptySlotCount).forEach(invokeTask);
              }, ctx.delayInMs);
            } else {
              misc.makeArrayOf(emptySlotCount).forEach(invokeTask);
            }
          };
          misc.makeArrayOf(ctx.concurrency).forEach(invokeTask);
          return () => void (isMounted = false);
        }
      },
      on: {
        "task.started": {
          actions: ["addRunning", "onStart"]
        },
        "task.resolved": {
          actions: ["addSuccess", "onSuccess"]
        },
        "task.rejected": {
          actions: ["addError", "onError"]
        },
        DONE: {
          target: "done",
          actions: "onDone"
        },
        UPDATE_CONCURRENCY: {
          actions: ["updateConcurrency", "forwardToScheduler"]
        }
      }
    },
    done: {
      type: "final"
    }
  },
  predictableActionArguments: true
}, {
  actions: {
    addRunning: xstate.assign({
      runningList: (ctx, event) => [...ctx.runningList, event.index]
    }),
    addSuccess: xstate.assign({
      resolvedList: (ctx, event) => [...ctx.resolvedList, {
        index: event.index,
        result: event.result
      }],
      runningList: (ctx, event) => ctx.runningList.filter(i => i !== event.index)
    }),
    addError: xstate.assign({
      rejectedList: (ctx, event) => [...ctx.rejectedList, {
        index: event.index,
        error: event.error
      }],
      runningList: (ctx, event) => ctx.runningList.filter(i => i !== event.index)
    }),
    onStart: (_ctx, event) => params.onStart?.(event.index),
    onSuccess: (_ctx, event) => params.onSuccess?.(event.result, event.index),
    onError: (_ctx, event) => params.onError?.(event.error, event.index),
    onDone: ctx => params.onDone?.(ctx),
    updateConcurrency: xstate.assign({
      concurrency: (_ctx, event) => event.concurrency
    }),
    forwardToScheduler: xstate.forwardTo("scheduler")
  }
});
const createPool = (taskList, {
  autoStart = true,
  ...params
} = {}) => {
  const machine = makePoolMachine({
    concurrency: 10,
    ...params,
    taskList
  });
  const service = xstate.interpret(machine).start();
  if (autoStart) service.send("START");
  return service;
};
const createAsyncPool = (taskList, {
  autoStart = true,
  ...params
} = {}) => {
  if (!taskList.length) return Promise.resolve([]);
  const service = createPool(taskList, {
    concurrency: 10,
    ...params
  });
  return new Promise(resolve => service.onDone(() => resolve(service.state.context.resolvedList.map(r => r.result))));
};
if (undefined) {
  const {
    it,
    expect,
    describe,
    vi
  } = undefined;
  describe("poolMachine", () => {
    it("should create a pool machine that will invoke onSuccess callbacks", () => new Promise(done => {
      const taskList = misc.makeArrayOf(10).map((_, i) => () => Promise.resolve(i + 1));
      const onSuccess = vi.fn();
      const machine = makePoolMachine({
        concurrency: 5,
        taskList,
        onSuccess
      });
      const service = xstate.interpret(machine).start();
      service.send("START");
      service.onDone(e => {
        expect(onSuccess).toHaveBeenCalledTimes(taskList.length);
        expect(service.state.context.resolvedList.map(r => r.result)).toEqual(taskList.map((_, i) => i + 1));
        done();
      });
    }));
    it("should create a pool and not auto start", () => {
      const taskList = misc.makeArrayOf(10).map((_, i) => () => Promise.resolve(i + 1));
      const service = createPool(taskList, {
        concurrency: 2,
        autoStart: false
      });
      expect(service.state.value).toBe("idle");
    });
    it("should create a pool that transitions to done instantly if passed an empty taskList", () => {
      expect(createPool([], {
        concurrency: 2
      }).state.value).toBe("done");
    });
    it("should create a pool that resolves instantly if passed an empty taskList", async () => {
      const results = await createAsyncPool([]);
      expect(results).toEqual([]);
    });
    it("should create a pool service that will invoke callbacks", () => new Promise(done => {
      const taskList = misc.makeArrayOf(10).map((_, i) => () => Promise.resolve(i + 1));
      const onSuccess = vi.fn();
      const onError = vi.fn();
      const onDone = vi.fn();
      const service = createPool(taskList, {
        concurrency: 2,
        onSuccess,
        onError,
        onDone
      });
      service.onDone(e => {
        expect(onSuccess).toHaveBeenCalledTimes(taskList.length);
        expect(service.state.context.resolvedList.map(r => r.result)).toEqual(taskList.map((_, i) => i + 1));
        expect(onError).not.toHaveBeenCalled();
        expect(onDone).toHaveBeenCalledTimes(1);
        done();
      });
    }));
    it("should create an async pool that will automatically resolve onDone with resolvedList", async () => {
      const taskList = misc.makeArrayOf(5).map((_, i) => () => Promise.resolve(i + 1));
      const result = await createAsyncPool(taskList, {
        concurrency: 2
      });
      expect(result).toEqual([1, 2, 3, 4, 5]);
    });
    it("should create an async pool that will automatically resolve even if some task failed", async () => {
      const taskList = misc.makeArrayOf(5).map((_, i) => () => i === 1 || i === 3 ? Promise.reject("boom-" + i) : Promise.resolve(i + 1));
      const onError = vi.fn((e, i) => expect(e).toBe("boom-" + i));
      const result = await createAsyncPool(taskList, {
        concurrency: 2,
        onError
      });
      expect(result).toEqual([1, 3, 5]);
      expect(onError).toHaveBeenCalledTimes(2);
    });
    it("should only execute tasks until concurrency is reached", async () => {
      const taskList = misc.makeArrayOf(16).map((_, i) => async () => {
        await misc.wait(i === 2 ? 20 : 10);
        return Promise.resolve(i + 1);
      });
      const service = createPool(taskList, {
        concurrency: 2
      });
      expect(service.state.context.resolvedList.map(r => r.result)).toEqual([]);
      await misc.wait(10);
      expect(service.state.context.resolvedList.map(r => r.result)).toEqual([1, 2]);
      await misc.wait(10);
      expect(service.state.context.resolvedList.map(r => r.result)).toEqual([1, 2, 4]);
      await misc.wait(10);
      expect(service.state.context.resolvedList.map(r => r.result)).toEqual([1, 2, 4, 3, 5]);
      service.send({
        type: "UPDATE_CONCURRENCY",
        concurrency: 4
      });
      await misc.wait(10);
      expect(service.state.context.resolvedList.map(r => r.result)).toEqual([1, 2, 4, 3, 5, 6, 7]);
      await misc.wait(10);
      expect(service.state.context.resolvedList.map(r => r.result)).toEqual([1, 2, 4, 3, 5, 6, 7, 8, 9, 10, 11]);
      await misc.wait(10);
      expect(service.state.context.resolvedList.map(r => r.result)).toEqual([1, 2, 4, 3, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]);
      await misc.wait(10);
      expect(service.state.context.resolvedList.map(r => r.result)).toEqual([1, 2, 4, 3, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16]);
    });
  });
  it("should wait given delayInMs between tasks", async () => {
    const taskList = misc.makeArrayOf(4).map((_, i) => async () => {
      await misc.wait(10);
      return Promise.resolve(i + 1);
    });
    const service = createPool(taskList, {
      concurrency: 2
    });
    expect(service.state.context.resolvedList.map(r => r.result)).toEqual([]);
    expect(service.state.context.runningList.map(i => i)).toEqual([0, 1]);
    await misc.wait(10);
    expect(service.state.context.resolvedList.map(r => r.result)).toEqual([1, 2]);
    expect(service.state.context.runningList.map(i => i)).toEqual([2, 3]);
    await misc.wait(10);
    expect(service.state.context.resolvedList.map(r => r.result)).toEqual([1, 2, 3, 4]);
    expect(service.state.context.runningList.map(i => i)).toEqual([]);
    const serviceWithDelayInBetween = createPool(taskList, {
      concurrency: 2,
      delayInMs: 50
    });
    expect(serviceWithDelayInBetween.state.context.resolvedList.map(r => r.result)).toEqual([]);
    expect(serviceWithDelayInBetween.state.context.runningList.map(i => i)).toEqual([0, 1]);
    await misc.wait(10);
    expect(serviceWithDelayInBetween.state.context.resolvedList.map(r => r.result)).toEqual([1, 2]);
    expect(serviceWithDelayInBetween.state.context.runningList.map(i => i)).toEqual([]);

    // waiting 50ms (delayInMs before starting)
    await misc.wait(10);
    expect(serviceWithDelayInBetween.state.context.resolvedList.map(r => r.result)).toEqual([1, 2]);
    await misc.wait(10);
    expect(serviceWithDelayInBetween.state.context.resolvedList.map(r => r.result)).toEqual([1, 2]);
    await misc.wait(10);
    expect(serviceWithDelayInBetween.state.context.resolvedList.map(r => r.result)).toEqual([1, 2]);
    await misc.wait(10);
    expect(serviceWithDelayInBetween.state.context.resolvedList.map(r => r.result)).toEqual([1, 2]);
    await misc.wait(10);

    // we waited the 50ms additional time from delayInMs so we will start the next tasks
    expect(serviceWithDelayInBetween.state.context.resolvedList.map(r => r.result)).toEqual([1, 2]);
    expect(serviceWithDelayInBetween.state.context.runningList.map(i => i)).toEqual([2, 3]);
    await misc.wait(10);
    // we should now have the tasks result
    expect(serviceWithDelayInBetween.state.context.resolvedList.map(r => r.result)).toEqual([1, 2, 3, 4]);
    expect(serviceWithDelayInBetween.state.context.runningList.map(i => i)).toEqual([]);
  });
}

const makeRetryMachine = ({
  callback,
  onRejected,
  ...ctx
}) => xstate.createMachine({
  id: "retry",
  initial: "pending",
  schema: {
    context: {},
    events: {}
  },
  tsTypes: {},
  context: {
    retryCount: 0,
    maxAttempt: 5,
    pauseDuration: 500,
    pauseCoeff: 1.2,
    ...ctx
  },
  states: {
    pending: {
      invoke: {
        id: "callback",
        src: () =>
        // safely promisify the function so we can handle errors even for sync functions
        new Promise(async (resolve, reject) => {
          try {
            resolve(await callback());
          } catch (error) {
            reject(error);
          }
        }),
        onDone: "success",
        onError: [{
          target: "error",
          cond: "hasReachedMaxAttempts"
        }, {
          target: "rejected"
        }]
      }
    },
    rejected: {
      entry: "onRejected",
      after: {
        RETRY: {
          actions: ["setPauseDuration", "incrementAttempt"],
          target: "pending"
        }
      }
    },
    error: {
      type: "final",
      data: (_ctx, event) => ({
        data: event.data,
        status: "error"
      })
    },
    success: {
      type: "final",
      data: (_ctx, event) => ({
        data: event.data,
        status: "success"
      })
    }
  }
}, {
  actions: {
    incrementAttempt: xstate.assign({
      retryCount: ctx => ctx.retryCount + 1
    }),
    setPauseDuration: xstate.assign({
      pauseDuration: ctx => ctx.pauseDuration * ctx.pauseCoeff
    }),
    onRejected: (ctx, event) => onRejected?.(event.data, ctx.retryCount)
  },
  guards: {
    hasReachedMaxAttempts: ctx => ctx.retryCount + 1 === ctx.maxAttempt
  },
  delays: {
    RETRY: ctx => ctx.pauseDuration
  }
});
async function retryIt(callback, options) {
  const retryMachine = makeRetryMachine({
    callback,
    ...options
  });
  const service = xstate.interpret(retryMachine).start();
  return new Promise((resolve, reject) => {
    service.onDone(event => {
      if (service.state.matches("success")) resolve(event.data.data);
      if (service.state.matches("error")) reject(event.data.data);
    });
  });
}
if (undefined) {
  const {
    it,
    expect,
    describe,
    vi
  } = undefined;
  describe("makeRetryMachine", () => {
    it("should resolve value", () => new Promise(done => {
      const machine = makeRetryMachine({
        callback: () => Promise.resolve("hello")
      });
      xstate.interpret(machine).onTransition((state, event) => {
        if (state.matches("success")) {
          expect(event.data).toBe("hello");
        }
      }).onDone(e => {
        const event = e;
        expect(event.data.status).toBe("success");
        expect(event.data.data).toBe("hello");
        done();
      }).start();
    }));
    it("should reject value & call onRejected", () => new Promise(done => {
      let retry = 0;
      const machine = makeRetryMachine({
        pauseDuration: 100,
        callback: async () => {
          throw new Error("boom");
        },
        onRejected: (err, retryCount) => {
          expect(err).toBeInstanceOf(Error);
          expect(err.message).toBe("boom");
          expect(retryCount).toBe(retry++);
        }
      });
      xstate.interpret(machine).onTransition((state, event) => {
        if (state.matches("error")) {
          expect(event.data.message).toBe("boom");
        }
      }).onDone(e => {
        const event = e;
        expect(event.data.status).toBe("error");
        expect(event.data.data.message).toBe("boom");
        done();
      }).start();
    }));
  });
  describe("retryIt", () => {
    it("will resolve value", () => {
      const value = retryIt(async () => "value");
      expect(value).resolves.toBe("value");
    });
    it("will reject value", () => {
      const value = retryIt(async () => {
        throw new Error("value");
      });
      expect(value).rejects.toThrow("value");
    });
    it("should retry the SYNC callback and invoke rejected callback", async () => {
      let attempt = 0;
      const callback = vi.fn(() => {
        attempt++;
        if (attempt === 1 || attempt === 2) {
          throw new Error("boom");
        }
        return Promise.resolve("hello");
      });
      const onRejected = vi.fn((err, retryCount) => {
        expect(err).toBeInstanceOf(Error);
        expect(err.message).toBe("boom");
        expect(retryCount).toBe(attempt - 1);
      });
      const result = await retryIt(callback, {
        pauseDuration: 100,
        onRejected
      });
      expect(result).toBe("hello");
      expect(callback).toHaveBeenCalledTimes(3);
      expect(onRejected).toHaveBeenCalledTimes(2);
    });
  });
}

exports.createAsyncPool = createAsyncPool;
exports.createPool = createPool;
exports.makePoolMachine = makePoolMachine;
exports.retryIt = retryIt;
