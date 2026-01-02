import * as React from "react";
export interface CreateContextOptions<Value, Initial extends Value = Value> {
    /**
     * If `true`, React will throw if context is `null` or `undefined`
     * In some cases, you might want to support nested context, so you can set it to `false`
     */
    strict?: boolean;
    /**
     * Error message to throw if the context is `undefined`
     */
    errorMessage?: string;
    /**
     * The display name of the context
     */
    name: string;
    /**
     * The display name of the context
     */
    initialValue?: Initial | undefined;
}
type CreateContextReturn<T> = [React.Provider<T>, () => T, React.Context<T>] & {
    Provider: React.Provider<T>;
    hook: () => T;
    Context: React.Context<T>;
    Consumer: React.Consumer<T>;
};
/**
 * Creates a named context, provider, and hook.
 *
 * @param options create context options
 */
export declare function createContextWithHook<ContextType>(options: CreateContextOptions<ContextType>): CreateContextReturn<ContextType>;
export declare function createContextWithHook<ContextType>(name: string, options?: CreateContextOptions<ContextType>): CreateContextReturn<ContextType>;
export {};
//# sourceMappingURL=createContextWithHook.d.ts.map