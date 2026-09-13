# Components, variants, and overrides

## Class composition is not conflict resolution

Use literal utility strings so Tailwind can discover them. Template concatenation, `clsx`, and `classnames` combine strings; they do not guarantee that a later conflicting Tailwind class overrides an earlier one. Define non-conflicting variants, or use an explicitly chosen merging policy.

For NativeWind v4/Tailwind v3, the `tailwind-merge` maintainer directs users to **v2.6.0** (`npm install tailwind-merge@^2.6.0`). Its current latest major targets Tailwind v4. NativeWind-specific/custom utility groups may need merger configuration and native verification; do not assume a web utility merger understands every extension.

## Typed button example

This example deliberately accepts ordinary React children, not Pressable's render-function children. Supporting a render function requires evaluating it with Pressable's state rather than placing the function inside Text.

```tsx
import type { ComponentProps, ReactNode } from 'react';
import { Pressable, Text } from 'react-native';
import { twMerge } from 'tailwind-merge';

const variants = {
  primary: { container: 'bg-blue-600 active:bg-blue-700', label: 'text-white' },
  secondary: { container: 'bg-zinc-200 dark:bg-zinc-800', label: 'text-zinc-900 dark:text-zinc-50' },
} as const;

type ButtonProps = Omit<ComponentProps<typeof Pressable>, 'children' | 'className'> & {
  children: ReactNode;
  variant?: keyof typeof variants;
  className?: string;
  labelClassName?: string;
};

export function Button({ children, variant = 'primary', className,
  labelClassName, disabled, accessibilityState, ...props }: ButtonProps) {
  const selected = variants[variant];
  return (
    <Pressable
      {...props}
      accessibilityRole={props.accessibilityRole ?? 'button'}
      disabled={disabled}
      accessibilityState={{ ...accessibilityState, disabled: Boolean(disabled) }}
      className={twMerge('rounded-md px-4 py-2', selected.container,
        disabled && 'opacity-50', className)}
    >
      <Text className={twMerge('font-semibold', selected.label, labelClassName)}>
        {children}
      </Text>
    </Pressable>
  );
}
```

Choose labels/content appropriate to the component; this is a text-labelled button, not a universal arbitrary-layout wrapper. Preserve focus, accessibility labels, disabled semantics, and adequate touch targets in the actual design. Test dark mode, pressed state, font scaling, and any consumer override.

Use a variants library only when its complexity solves a real need. `class-variance-authority` is the package name for the commonly used `cva` function; do not install a similarly named package by guessing. Reuse the app's established variant system before adding another dependency.

Sources reviewed 2026-09-13: [NativeWind custom components](https://www.nativewind.dev/docs/guides/custom-components), [tailwind-merge compatibility](https://github.com/dcastil/tailwind-merge).
