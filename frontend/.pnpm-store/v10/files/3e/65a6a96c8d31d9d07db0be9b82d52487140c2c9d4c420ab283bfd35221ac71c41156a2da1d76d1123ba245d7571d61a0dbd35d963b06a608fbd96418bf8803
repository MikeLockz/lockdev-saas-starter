import { AnyFunction } from "../typings";
interface Context {
    retryCount: number;
    maxAttempt: number;
    pauseDuration: number;
    pauseCoeff: number;
}
interface MakeRetryMachineParams<Result = any> extends Partial<Pick<Context, "maxAttempt" | "pauseDuration" | "pauseCoeff">> {
    callback: AnyFunction<Promise<Result>>;
    onRejected?: (error: any, retryCount: number) => void;
}
export type RetryDoneEvent<Result = any, Status extends "success" | "error" = any> = Status extends "success" ? {
    data: Result;
    status: "success";
} : {
    data: unknown;
    status: "error";
};
export declare function retryIt<Result = any>(callback: MakeRetryMachineParams<Result>["callback"], options?: Omit<MakeRetryMachineParams, "callback">): Promise<Result>;
export {};
//# sourceMappingURL=retryMachine.d.ts.map