# 【TiDB】用語を整理しながら学ぶTiDB

## はじめに

この記事では 用語を整理しながらTiDBを学習していく記事です。
主な内容としては学習したときのメモを中心に書きます。（忘れやすいことなど）
誤りなどがあれば書き直していく予定です。

ところどころで[PingCAPさん](https://pingcap.co.jp/)のサイトを引用してまとめていきます。

## TiDBとは

TiDBはHTAPワークロードをサポートするオープンソースの分散SQLデータベースです。
世界1600社以上の商用環境が採用しています。また、TiDB Serverlessを利用するとサーバレスにDB環境を構築できます。

[公式のOverview](https://docs.pingcap.com/ja/tidb/stable/overview)では下記のように説明があります。

> TiDB (/'taɪdiːbi:/、「Ti」は Titanium の略) は、ハイブリッド トランザクションおよび分析処理 (HTAP) ワークロードをサポートするオープンソースの分散 SQL データベースです。 MySQL と互換性があり、水平スケーラビリティ、強力な一貫性、高可用性を備えています。 TiDB の目標は、OLTP (オンライン トランザクション処理)、OLAP (オンライン分析処理)、および HTAP サービスをカバーするワンストップ データベース ソリューションをユーザーに提供することです。 TiDB は、高可用性と大規模データの強力な一貫性を必要とするさまざまなユースケースに適しています。

HTAPワークロード？オープンソースの分散SQLデータベース？水平スケーラビリティ、強力な一貫性、高可用性？
OLTP (オンライン トランザクション処理)、OLAP (オンライン分析処理)、および HTAP サービスをカバーするワンストップ データベース ソリューションをユーザーに提供？

なるほど。わかりそうでわからない。。。。

## 前提知識

### HTAPワークロードとは

TiDBを知るにはHTAPとは何かを知る必要があります。

[HTAP クエリ - PingCAP Docs](https://docs.pingcap.com/ja/tidb/v6.1/dev-guide-hybrid-oltp-and-olap-queries)では下記のように説明があります。

> HTAP は Hybrid Transactional and Analytical Processing の略です。従来、データベースは多くの場合、トランザクションまたは分析のシナリオ向けに設計されているため、データ プラットフォームは多くの場合、トランザクション処理と分析処理に分割する必要があり、データをトランザクション データベースから分析データベースに複製して、分析クエリに迅速に応答する必要があります。 TiDB データベースはトランザクションタスクと分析タスクの両方を実行できるため、データプラットフォームの構築が大幅に簡素化され、ユーザーはより新しいデータを分析に使用できるようになります。

多くの場合においてデータストアとしてのアプリケーション用のDBと分析用のDBを分けます。
AWSの中でもAmazon RDSに触れたことがある人であればわかるかもしれませんが
RDSでは「分析用のワークロード用にリードレプリカを作成して提供する」というソリューションあるいはベストプラクティスがあります。

リードレプリカを作ることにより「分析ワークロードのスケーラビリティを確保しつつ、アプリケーションワークロードのスループットを確保する」ということです。
つまり、多くの場合においてアプリケーション用のDBにはOLTP、分析用のDBにはOLAPが必要です。

ポイントとしてはHTAP = OLTP + OLAPということになります。

### OLTP

Online Transactional Processingの略です。トランザクションが必要な処理で使います。
たとえば、商品の注文処理などのプロセスにはOLTPが必要です。

### OLAP

Online Analytical Processingの略です。集計と分析が必要な処理で使います。
たとえば、分析処理に必要です。

### 分散SQLデータベース

これらの仕組み（HTAP）を複数のデータベースマシンで管理しています。
ここで複数のマシンでデータベースを管理するデータベースのことを分散（分散型）データベースといい、TiDBの場合は分散SQLデータベースということになります。
分散データベースというとNoSQLとなりますが、分散`SQL`データベースであるということがポイントです。つまりはNewSQLです。

### NewSQLとは

高い可用性と水平方向の拡張性があり、SQLインタフェースを併せ持つデータベースあるいは総称名です。

## 本題に戻ってTiDBとは

つまり、TiDBとはHTAPを備えた分散SQLデータベースであり、NewSQLです。
なお、同じ分散SQLデータベースとしてCloud SpannerやCockroachDBが存在します。
Cloud Spannerは言わずと知れたGoogleが社内で利用している分散SQLデータベースです。

## TiDBの特徴

TiDBは主に下記に示す3つのコンポーネントで構成されています。

- PD (Placement Driver)
- TiKV
- TiDB

なお、リアルタイムHTAPを実現する際にはTiFlashも併用しています。

### PD (Placement Driver)とは

Placementとあるように分散SQLであるため、クラスターを管理する必要があります。
TiDBではTiKVで構成されたクラスターを管理する機能に位置付けられています。

どのようなアーキテクチャであるかどうかについては[公式ブログ](https://pingcap.co.jp/deep-dive-into-tikv/
)に記載があります。

> Placement Driver (PD)：PDはTiKVシステムの頭脳であり、ノード、ストア、リージョンのマッピングに関するメタデータを管理し、データ配置と負荷分散の決定を行います。PDは定期的にレプリケーションの制約をチェックし、負荷とデータのバランスを自動的に調整します。

負荷とデータのバランスをとるバランサー的なポジションをとるものだとわかります。ではPDに管理されるTiKVとはなんでしょうか。

### TiKVとは

TiDBにはリアルタイムHTAPを実現するために二つのストレージエンジンを備えています。その一つが行ベースのストレージエンジンであるTiKVです。
TiKVはデータを保管する役割があります。PDがどこにデータを挿入するかを判断したあとにKV（Key-Value）でデータを保管します。

なお、リアルタイムHTAPを実現する際に必要となる列ベースのストレージエンジンはTiFlashといいます。
TiFlashは主に分析処理に利用されます。

### TiDB（構成要素としてのTiDB）とは

PDとTiKVの役割がわかったところでではTiDBはどういう役割があるのでしょうか。
※わかりにくいかもしれませんが、システム全体のことをTiDBと呼ぶこともあれば、一部をTiDBと呼ぶこともあります。

TiDBはSQLを解釈してストレージエンジン（TiKVまたはTiFlash）につなげる役割があります。

TiDBは「MySQLプロトコルの接続エンドポイントを外部に公開するステートレスSQLレイヤー」として機能します。
実行されたSQLを解釈して最適化し、実行プランを作成します。

なお、実態はサーバになりますが、データの保存はストレージエンジンのTiKVやTiFlashが担うため
構成要素としてのTiDBはデータを保存しません。

## それとなくわかったけど触るにはどうした良いの？

TiDBについて触りが理解できたところでとりあえず触りたくなってきたと思います。
触り方は公式ガイドのクイックスタートを見ることですぐに始められます。

[TiDB データベース プラットフォームのクイック スタート ガイド](https://docs.pingcap.com/ja/tidb/stable/quick-start-with-tidb)

手を動かすのがこわい人、もしくは知識だけでも身につけておきたいという人には[PingCAP Certified TiDB](https://www.pingcap.com/education/certification/)もあります。

## PingCAP Certified TiDBについて

PingCAP Certified TiDBについては見ていきましょう。2023年11月においては4つの資格があるようです。

- Foundational Certification
  - PingCAP Certified TiDB Practitioner
- Advanced Certifications
  - PingCAP Certified TiDB Associate Database Administrator
  - PingCAP Certified SQL Developer
  - PingCAP Certified TiDB Professional Database Administrator

各資格について見ていきましょう。

### PingCAP Certified TiDB Practitioner

TiDBの基本概念、用語、ユースケースを理解していることを確認する資格です。
TiDBやデータベース技術の経験が浅くても、TiDBに興味のある方ならどなたでも取得できるエントリーレベルの資格であり、完全無料の認定資格です。
合格するまで何度でも再受験することができます

[PingCAP Certified TiDB Practitioner](https://www.pingcap.com/education/certification/pingcap-certified-tidb-practitioner/)

### PingCAP Certified TiDB Associate Database Administrator

TiDBとTiDBクラウド上でワークロードを展開、管理、運用するための重要なスキルを証明する資格です。
試験時間80分、180 USD
多肢選択式、複数回答式、穴埋め式となっているそうです。

PDFで試験ガイドがあるので受験する方は見ておくとよいでしょう。

[PingCAP Certified TiDB Associate Database Administrator](https://www.pingcap.com/education/certification/pingcap-certified-tidb-associate/)

### PingCAP Certified SQL Developer

TiDBのユニークな機能の使用、TiDBを使用した高可用性で弾力性のあるアプリケーションの作成
データベースを使用する際のベストプラクティスに従うことについて、開発者のスキルと知識を証明する資格です。

試験時間90分、180 USD
選択式または複数回答式となっているそうです。

[PingCAP Certified SQL Developer](https://www.pingcap.com/education/certification/pingcap-certified-sql-developer/)

### PingCAP Certified TiDB Professional Database Administrator

この資格では下記のようなことが問われます。

- TiDBの原則
- 大規模なTiDBクラスタの管理
- TiDB Lightning
- TiDB Data Migration
- TiCDC
- sync-diff-inspectorなどのTiDBツール
- トラブルシューティングのスキルに関する熟練度

試験時間80分、240 USD
多肢選択式、多肢選択式、順序選択式となっているそうです。

また、プロフェッショナル資格については受験資格として`PingCAP Certified TiDB Associate`に合格している必要があります。

[PingCAP Certified TiDB Professional Database Administrator](https://www.pingcap.com/education/certification/pingcap-certified-tidb-professional-database-administrator/)

## これから学習していくにあたって

試験がいくつかあるがわかりました。「自分がどれに向いているのだろう」、「何から始めたら良いかわからない」という人
下記に示すものを見ていくと良いでしょう。

また、TiDBを提供するPingCAP JapanさんはYouTube公式チャンネルで動画を公開しています。
[PingCAP - Japan](https://www.youtube.com/@pingcap-japan3763)

加えて、2023年7月7日に開催された[TiDB User Day](https://pingcap.co.jp/tidb-user-day-2023-thank-you/)においてはさまざまな事例が紹介されています。

## ワークショップ

とりあえず、手を動かしてみたい人向けです。
[TiDB公式トレーニング](https://pingcap.co.jp/education/)

## 書籍

[Software Design 2023年8月号](https://gihyo.jp/magazine/SD/archive/2023/202308)にTiDBの特集があります。
筆者の私も読みましたが、最初に読むにはちょうどいい内容だと思いました。

※[e-book](https://gihyo.jp/dp/ebook/2023/978-4-297-13453-2)はここ

## まとめ

今回は分散SQLデータベースのTiDBを見ていきました。
新しいDB分野のNewSQLについてはまだ勉強中ですが、TiDBがすごいデータベースであることは
理解できたかなと思います。なお、大規模なデータベースほど威力を発揮する特徴があるのでそういった方は積極的に試してみると良いかもしれません。

ちなみに筆者の私はTiDB User Dayで初めてTiDBを知り、Software Design 2023年8月号で入門しました。ハンズオンなどはこれからになりますが、身近で活用事例も見ているので理解が捗りました。

## 参考

- [TiDB Introduction](https://docs.pingcap.com/ja/tidb/stable)
- [TiDB Feautures - TiDB](https://docs.pingcap.com/ja/tidb/stable/basic-features)
- [HTAPとは何か](https://pingcap.co.jp/what-is-htap/)
- [HTAPデータベースを構築してデータプラットフォームをシンプルにする方法](https://pingcap.co.jp/blog-how-we-build-an-htap-database-that-simplifies-your-data-platform/)
- [TiDBのアーキテクチャ](https://docs.pingcap.com/ja/tidb/stable/tidb-architecture)
- [TiDBオートスケーリング：クラウドネイティブアプリケーション用の分散SQLを使用する理由](https://pingcap.co.jp/tidb-auto-scaling-distributed-sql-cloud-native-apps/)
