# Using Expo SDK in bare React Native apps (without Expo)

## When to use
- you have a “bare” React Native project (not an Expo managed app)
- you want Superwall’s Expo SDK anyway (it’s built as an Expo Module)

## Steps (high level)

### 1) Install Expo Modules
```bash
npx install-expo-modules@latest
```

### 2) Install Superwall
```bash
npx expo install expo-superwall
```

### 3) iOS setup
- Open the iOS project in Xcode.
- Set **deployment target to iOS 15.1+**.
- Install pods:

```bash
cd ios
pod install
```

### 4) Android setup
- Ensure your app targets **minSdkVersion 21+** in `android/build.gradle`.

## Sources
- https://superwall.com/docs/expo/guides/bare-react-native
