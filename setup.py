from setuptools import setup

setup(
    name='Geppetto',
    version='0.1.0',
    python_requires='>=3.6',  

    description='Geppetto is a Slack bot that integrates with OpenAIs and DALL-E-3 models.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',

    author='',
    author_email='',

    url='https://github.com/CoinFabrik/geppetto',

    install_requires=[
        'certifi>=2023.11.17',
        'openai>=1.4.0',
        'python-dotenv==1.0.0',
        'slack-bolt>=1.18.1',
        'slack-sdk>=3.26.1',
        'Pillow>=10.1.0',
    ],

    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
        'Topic :: Chatbot'
    ],

    entry_points={
        'console_scripts': [
            'geppetto = main:main',
        ],
    },

    keywords='geppetto slack openai chatbot',

    license='Geppetto is licensed and distributed under a MIT license.',
)