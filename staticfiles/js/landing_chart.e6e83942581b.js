/** @format */

"use strict"

$(document).ready(function () {
  function get_leave_balance(leave_type) {
    $.ajax({
      url: "/selfservice/LeaveBalance/",
      type: "GET",
      data: {
        leave_type: leave_type,
        csrfmiddlewaretoken: "{{ csrf_token }}",
      },
      success: function (data) {
        $("#annual_balance").empty().append(data)
      },
      error: function (xhr, textStatus, errorThrown) {
        console.log(xhr.responseText)
      },
    })
  }

  get_leave_balance("ANNUAL")

  function FnGetAnnualLeaveDashboard(leave_type) {
    $.ajax({
      url: "/selfservice/FnGetAnnualLeaveDashboard/",
      type: "GET",
      data: {
        csrfmiddlewaretoken: "{{ csrf_token }}",
      },
      success: function (data) {
        createChart(
          data["balanceBF"],
          data["daysTakenToDate"],
          data["recalledDays"]
        )
        $("#max_overdraft").empty().append(data["availableMaxOverdraft"])
        $("#leave_earned").empty().append(data["leaveEarnedToDate"])
      },
      error: function (xhr, textStatus, errorThrown) {
        console.log(xhr.responseText)
      },
    })
  }

  FnGetAnnualLeaveDashboard()

  function createChart(balanceForward, daysToDate, recalledDays) {
    var statistics_chart = document.getElementById("myChart").getContext("2d")

    var myChart = new Chart(statistics_chart, {
      type: "line",
      data: {
        labels: [
          "Balance brought forward",
          "Days Taken To Date",
          "Recalled Days",
        ],
        datasets: [
          {
            label: "Leave Statistics",
            data: [balanceForward, daysToDate, recalledDays],
            borderWidth: 5,
            borderColor: "#e30d0e",
            backgroundColor: "transparent",
            pointBackgroundColor: "#fff",
            pointBorderColor: "#000",
            pointRadius: 8,
          },
        ],
      },
      options: {
        legend: {
          display: false,
        },
        scales: {
          yAxes: [
            {
              gridLines: {
                display: false,
                drawBorder: false,
              },
              ticks: {
                stepSize: 21,
              },
            },
          ],
          xAxes: [
            {
              gridLines: {
                color: "#fbfbfb",
                lineWidth: 2,
              },
            },
          ],
        },
      },
    })
  }
})
