import ReactECharts from "echarts-for-react";

type Props = {
  title: string;
  option: object;
};

export function ChartCard({ title, option }: Props) {
  return (
    <section className="card chart-card">
      <div className="section-head">
        <h2>{title}</h2>
      </div>
      <ReactECharts option={option} style={{ height: 320 }} />
    </section>
  );
}

