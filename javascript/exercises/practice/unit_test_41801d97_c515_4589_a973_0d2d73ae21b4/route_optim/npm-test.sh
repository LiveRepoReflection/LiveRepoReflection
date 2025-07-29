#!/bin/bash

npm install -g jest

sed -i 's/\bxtest(/test(/g' *.spec.js
npm i 
npm run test
