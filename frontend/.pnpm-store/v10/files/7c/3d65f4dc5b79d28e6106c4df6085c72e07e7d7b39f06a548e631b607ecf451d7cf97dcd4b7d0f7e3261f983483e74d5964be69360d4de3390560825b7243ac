import { PartialBy } from "../typings";
export declare const makePoolMachine: <Return = any>(params: MakePoolMachineParams<Return>) => import("xstate").StateMachine<Context<Return>, any, {
    type: "START";
} | {
    type: "task.started";
    index: number;
} | {
    type: "task.resolved";
    index: number;
    result: Return;
} | {
    type: "task.rejected";
    index: number;
    error: any;
} | {
    type: "UPDATE_CONCURRENCY";
    concurrency: number;
} | {
    type: "DONE";
}, {
    value: any;
    context: Context<Return>;
}, import("xstate").BaseActionObject, import("xstate").ServiceMap, import("xstate").ResolveTypegenMeta<import("./poolMachine.typegen").Typegen0, {
    type: "START";
} | {
    type: "task.started";
    index: number;
} | {
    type: "task.resolved";
    index: number;
    result: Return;
} | {
    type: "task.rejected";
    index: number;
    error: any;
} | {
    type: "UPDATE_CONCURRENCY";
    concurrency: number;
} | {
    type: "DONE";
}, import("xstate").BaseActionObject, import("xstate").ServiceMap>>;
interface Context<Return> extends Pick<MakePoolMachineParams<Return>, "concurrency" | "delayInMs"> {
    runningList: number[];
    resolvedList: Array<{
        index: number;
        result: Return;
    }>;
    rejectedList: Array<{
        index: number;
        error: any;
    }>;
}
type Thunk<Return = any> = () => Promise<Return>;
interface MakePoolMachineParams<Return = any> {
    taskList: Array<Thunk<Return>>;
    concurrency: number;
    delayInMs?: number;
    onStart?: (index: number) => void;
    onSuccess?: (result: Return, index: number) => void;
    onError?: (error: any, index: number) => void;
    onDone?: (ctx: Context<Return>) => void;
}
export declare const createPool: <Return = any>(taskList: Thunk<Return>[], { autoStart, ...params }?: CreatePoolParams<Return>) => import("xstate").Interpreter<Context<Return>, any, {
    type: "START";
} | {
    type: "task.started";
    index: number;
} | {
    type: "task.rejected";
    index: number;
    error: any;
} | {
    type: "UPDATE_CONCURRENCY";
    concurrency: number;
} | {
    type: "DONE";
} | {
    type: "task.resolved";
    index: number;
    result: Return;
}, {
    value: any;
    context: Context<Return>;
}, import("xstate").ResolveTypegenMeta<import("./poolMachine.typegen").Typegen0, {
    type: "START";
} | {
    type: "task.started";
    index: number;
} | {
    type: "task.rejected";
    index: number;
    error: any;
} | {
    type: "UPDATE_CONCURRENCY";
    concurrency: number;
} | {
    type: "DONE";
} | {
    type: "task.resolved";
    index: number;
    result: Return;
}, import("xstate").BaseActionObject, import("xstate").ServiceMap>>;
export declare const createAsyncPool: <Return = any>(taskList: Thunk<Return>[], { autoStart, ...params }?: CreatePoolParams<Return>) => Promise<Return[]>;
interface CreatePoolParams<Return = any> extends Omit<PartialBy<MakePoolMachineParams<Return>, "concurrency" | "delayInMs">, "taskList"> {
    autoStart?: boolean;
}
export {};
//# sourceMappingURL=poolMachine.d.ts.map