module.exports = {
	env: {
		browser: true,
		es2021: true,
		node: true,
	},
	extends: ['airbnb', 'prettier', 'plugin:prettier/recommended'],
	parser: '@typescript-eslint/parser',
	parserOptions: {
		ecmaFeatures: {
			jsx: true,
		},
		ecmaVersion: 12,
		sourceType: 'module',
	},
	settings: {
		'import/resolver': {
			node: {
				extensions: ['.js', '.jsx', '.ts', '.tsx'],
				paths: ['src'],
			},
		},
	},
	plugins: ['prettier'],
	rules: {
		'prettier/prettier': ['error'],
		'react/jsx-filename-extension': [2, { extensions: ['.js', '.jsx', '.ts', '.tsx'] }],
		'import/extensions': 'off',
		'no-use-before-define': 'off',
		'no-unused-vars': 'off',
		'no-console': 'off',
	},
};
