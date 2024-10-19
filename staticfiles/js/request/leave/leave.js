/** @format */

$(document).ready(function () {
  var headerCode = "0"

  const $next_one = $("#next_one")
  const $header_step = $("#header_step")
  const $attachments_step = $("#attachments_step")
  const $Attachment_Prev = $("#Attachment_Prev")
  const $attachment_next = $("#attachment_next")
  const $attachmentForm = $("#leave_attachment_form")
  const $Attachment_Toggle = $("#Attachment_Toggle")
  const $approvalForm = $("#application_submit")
  const $headerForm = $("#headerForm")
  const $header_spinner = $("#header-spinner")
  const $leaveBalance = $("#leaveBalance")
  const $leaveTypeInput = $("#leaveType")
  const $BasedOnPlannerInput = $("#BasedOnPlanner")
  const $plannerStartDate = $("#plannerStartDate")
  const $startDateInput = $("#start-date")
  const $startDateCol = $("#startDateCol")
  const $planner_col = $("#planner_col")
  const $isReturnSameDay = $("#isReturnSameDay")
  const $Approvers_Data_Step = $("#Approvers_Data_Step")
  const $CancelApprovalForm = $("#application_cancel")
  const $myAction = $("#myAction")
  const $daysApplied = $("#daysApplied")
  const $daysAppliedCol = $("#daysAppliedCol")
  const $applicationNo = $("#applicationNo")
  const $whichHalfOfDay = $("#whichHalfOfDay")
  const $whichHalfOfDayCol = $("#whichHalfOfDayCol")
  const today = new Date().toISOString().split("T")[0]
  const $Reliever_Form = $("#reliever_form")
  const $RelieverInput = $("#Reliever")
  const $relievers_table = $("#relievers_table")

  $startDateInput.prop("min", today)

  $BasedOnPlannerInput.on("change", function () {
    if (this.value === "True") {
      $startDateInput.prop("disabled", true)
      $startDateCol.hide()
      $plannerStartDate.prop("disabled", false)
      $planner_col.show(600)
      $isReturnSameDay.prop("disabled", true)
      $daysApplied.prop("disabled", true)
    } else if (this.value === "False") {
      $plannerStartDate.prop("disabled", true)
      $startDateCol.show(600)
      $startDateInput.prop("disabled", false)
      $planner_col.hide()
      $isReturnSameDay.prop("disabled", false)
    }
  })

  $isReturnSameDay.on("change", function () {
    if (this.value === "False") {
      $daysApplied.prop("disabled", false)
      $daysAppliedCol.show(600)
      $whichHalfOfDay.prop("disabled", true)
      $whichHalfOfDayCol.hide()
    } else if (this.value === "True") {
      $daysApplied.prop("disabled", true)
      $daysAppliedCol.hide()
      $whichHalfOfDayCol.show(600)
      $whichHalfOfDay.prop("disabled", false)
    }
  })

  function get_leave_balance(leave_type) {
    $.ajax({
      url: "/selfservice/LeaveBalance/",
      type: "GET",
      data: {
        leave_type: leave_type,
      },
      success: function (data) {
        $leaveBalance.val(data + " " + "days")
      },
      error: function (xhr, textStatus, errorThrown) {
        console.log(xhr.responseText)
      },
    })
  }

  $leaveTypeInput.change(function () {
    var selectedValue = $(this).val()
    get_leave_balance(selectedValue)
  })

  $plannerStartDate.on("change", function (e) {
    e.preventDefault()
    var planner_date = $plannerStartDate.val()

    if (planner_date != null) {
      $.ajax({
        type: "get",
        url: "/selfservice/NumberOfDaysFilter/",
        dataType: "json",
        data: {
          planner_date: planner_date,
        },
        success: function (response) {
          $daysApplied.val(response)
          $daysApplied.prop("disabled", true)
        },
        error: function (response) {
          console.log("Something went wrong")
        },
      })
    } else {
    }
  })

  $headerForm.on("submit", (e) => {
    e.preventDefault()

    if ($leaveTypeInput.val() === "") {
      alert("Please fill in all required fields.")
      return false
    }
    $header_spinner.show()
    $.ajax({
      type: "POST",
      url: "/selfservice/Leave",
      data: {
        applicationNo: $applicationNo.val(),
        leaveType: $leaveTypeInput.val(),
        usePlanner: $BasedOnPlannerInput.val(),
        plannerStartDate: $plannerStartDate.val(),
        LeaveStartDate: $startDateInput.val(),
        daysApplied: $daysApplied.val(),
        isReturnSameDay: $isReturnSameDay.val(),
        whichHalfOfDay: $whichHalfOfDay.val(),
        myAction: $myAction.val(),
        csrfmiddlewaretoken: $("input[name=csrfmiddlewaretoken]").val(),
      },
      success: function (response) {
        if (response["response"]) {
          iziToast.show({
            theme: "dark",
            backgroundColor: "#239B56",
            icon: "las la-check-circle",
            title:
              "Leave" +
              " " +
              response["response"] +
              " " +
              "created successfully",
            position: "topRight",
            progressBarColor: "#F4F6F7",
          })
          $header_spinner.hide()
          $(
            "#leaveType,#usePlanner, #plannerStartDate, #start-date, #daysApplied, #isReturnSameDay,#myAction, #whichHalfOfDay"
          ).val("")
          headerCode = response["response"]
          filter_list(headerCode)
          $header_step.hide()
          $attachments_step.show()
        } else if (response["error"]) {
          iziToast.show({
            theme: "dark",
            icon: "las la-exclamation",
            title: response["error"],
            position: "topRight",
            progressBarColor: "#ff0800",
          })
          $header_spinner.hide()
        }
      },
      error: function (error) {
        console.log(error)
        $header_spinner.hide()
      },
    })
  })

  $Reliever_Form.on("submit", (e) => {
    e.preventDefault()

    var Reliever = $RelieverInput.val()

    if (Reliever === "") {
      alert("Please fill in all required fields.")
      return false
    }
    $header_spinner.show()
    $.ajax({
      type: "POST",
      url: "/selfservice/FnLeaveReliever/" + headerCode + "/",
      data: {
        Reliever: Reliever,
        myAction: $("#reliever_action").val(),
        csrfmiddlewaretoken: $("input[name=csrfmiddlewaretoken]").val(),
      },
      success: function (response) {
        if (response["response"]) {
          iziToast.show({
            theme: "dark",
            backgroundColor: "#239B56",
            icon: "las la-check-circle",
            message: "Reliever created successfully",
            position: "topRight",
            progressBarColor: "#F4F6F7",
          })
          $header_spinner.hide()
          $("#Reliever").val("")
          RelieverData(headerCode)
        } else if (response["error"]) {
          iziToast.show({
            theme: "dark",
            icon: "las la-exclamation",
            title: "Error",
            message: response["error"],
            position: "topRight",
            progressBarColor: "#ff0800",
          })
          $header_spinner.hide()
        }
      },
      error: function (error) {
        console.log(error)
        $header_spinner.hide()
      },
    })
  })

  $attachmentForm.on("submit", (e) => {
    e.preventDefault()

    $header_spinner.show()
    var formData = new FormData($attachmentForm[0])

    let attachments = $("#attachments")[0]
    for (let i = 0; i < attachments.files.length; i++) {
      formData.append("attachment", attachments.files[i])
    }
    formData.append("tableID", 50520)

    $.ajax({
      url: "/selfservice/Attachments/" + headerCode + "/",
      type: "POST",
      data: formData,
      processData: false,
      contentType: false,
      headers: {
        "X-CSRFToken": $('input[name="csrfmiddlewaretoken"]').val(),
      },
      success: function (data) {
        $("#attachments").val("")
        $header_spinner.hide()
        if (data["success"] == true) {
          iziToast.show({
            theme: "dark",
            backgroundColor: "#239B56",
            icon: "las la-check-circle",
            message: "Uploaded successfully",
            position: "topRight",
            progressBarColor: "#F4F6F7",
          })
          Load_Attachments(headerCode)
          $("#attachments_row").show(1000)
        } else {
          iziToast.show({
            theme: "dark",
            icon: "las la-exclamation",
            title: "Error",
            message: "Upload failed: " + data,
            position: "topRight",
            progressBarColor: "#ff0800",
          })
        }
      },
      error: function (xhr, textStatus, errorThrown) {
        console.log(xhr.responseText)
        $header_spinner.hide()
      },
    })
  })

  $approvalForm.on("submit", (e) => {
    e.preventDefault()
    $header_spinner.show(200)
    console.log(headerCode)
    $.ajax({
      type: "POST",
      url: "/selfservice/ApprovalRequest/",
      data: {
        service_name: "FnRequestLeaveApproval",
        headerCode: headerCode,
        csrfmiddlewaretoken: $("input[name=csrfmiddlewaretoken]").val(),
      },
      success: function (data) {
        $header_spinner.hide()

        if (data["success"] == true) {
          iziToast.show({
            theme: "dark",
            backgroundColor: "#239B56",
            icon: "las la-check-circle",
            message: data["message"],
            position: "topRight",
            progressBarColor: "#F4F6F7",
          })
          ApproversData(headerCode)
          $(".attach_step").addClass("completed")
          $(".submitted_step").addClass("completed")
          $attachments_step.hide()
          $Approvers_Data_Step.show()
        } else {
          iziToast.show({
            theme: "dark",
            icon: "las la-exclamation",
            title: "Error",
            message: data["error"],
            position: "topRight",
            progressBarColor: "#ff0800",
          })
        }
      },
      error: function (error) {
        console.log(error)
        $header_spinner.hide()
      },
    })
  })

  $CancelApprovalForm.on("submit", (e) => {
    e.preventDefault()
    $.ajax({
      type: "POST",
      url: "/selfservice/CancelApproval/",
      data: {
        service_name: "FnCancelLeaveApproval",
        headerID: headerCode,
        csrfmiddlewaretoken: $("input[name=csrfmiddlewaretoken]").val(),
      },
      success: function (data) {
        if (data["success"] == true) {
          iziToast.show({
            theme: "dark",
            backgroundColor: "#239B56",
            icon: "las la-check-circle",
            message: data["message"],
            position: "topRight",
            progressBarColor: "#F4F6F7",
          })
          ApproversData(headerCode)
          $(".attach_step").removeClass("completed")
          $(".submitted_step").removeClass("completed")
          $Approvers_Data_Step.hide()
          $attachments_step.show()
        } else {
          iziToast.show({
            theme: "dark",
            icon: "las la-exclamation",
            title: "Error",
            message: data["error"],
            position: "topRight",
            progressBarColor: "#ff0800",
          })
        }
      },
      error: function (error) {
        console.log(error)
      },
    })
  })

  function RelieverData(pk) {
    $.ajax({
      url: "/selfservice/FnLeaveReliever/" + pk + "/",
      type: "GET",
      dataType: "json",
      success: function (data) {
        var tableBody = $("#relievers_table tbody")
        tableBody.empty()

        for (var i = 0; i < data.length; i++) {
          var LeaveCode = data[i].LeaveCode
          var StaffNo = data[i].StaffNo
          var StaffName = data[i].StaffName
          var ShortcutDimension1Code = data[i].ShortcutDimension1Code

          var row = $("<tr>")
          row.append($("<td>").text(LeaveCode))
          row.append($("<td>").text(StaffNo))
          row.append($("<td>").text(StaffName))
          row.append($("<td>").text(ShortcutDimension1Code))

          var deleteButton = $("<button>")
            .text("Delete")
            .addClass("btn btn-danger delete-btn")
            .data("staffNo", StaffNo)
            .data("leaveCode", LeaveCode)
          var deleteColumn = $("<td>").append(deleteButton)
          row.append(deleteColumn)
          tableBody.append(row)
        }
        // initialize DataTables for each table
        if (!$.fn.DataTable.isDataTable("#relievers_table")) {
          $("#relievers_table").DataTable({
            pageLength: 5,
            order: [[0, "desc"]],
          })
        }
        $(".delete-btn").on("click", function () {
          var staffNo = $(this).data("staffNo")
          var leaveCode = $(this).data("leaveCode")
          $header_spinner.show()
          $.ajax({
            url: "/selfservice/FnLeaveReliever/" + leaveCode + "/",
            type: "POST",
            data: {
              Reliever: staffNo,
              myAction: "delete",
              csrfmiddlewaretoken: $("input[name=csrfmiddlewaretoken]").val(),
            },
            success: function (response) {
              if (response["response"]) {
                iziToast.show({
                  theme: "dark",
                  backgroundColor: "#239B56",
                  icon: "las la-check-circle",
                  message: "Reliever deleted successfully",
                  position: "topRight",
                  progressBarColor: "#F4F6F7",
                })
                $header_spinner.hide()
                RelieverData(headerCode)
              } else if (response["error"]) {
                iziToast.show({
                  theme: "dark",
                  icon: "las la-exclamation",
                  title: "Error",
                  message: response["error"],
                  position: "topRight",
                  progressBarColor: "#ff0800",
                })
                $header_spinner.hide()
              }
            },
            error: function (error) {
              console.log(error)
              $header_spinner.hide()
            },
          })
        })
      },
      error: function (xhr, status, error) {
        console.log("Error:", error)
      },
    })
  }

  function filter_list(pk) {
    var query = "/QyLeaveApplications"
    var filter_one = "Application_No"
    var filter_two = "User_ID"
    var filter_two_type = "user"

    $.ajax({
      url: "/selfservice/filter_list/" + pk,
      type: "GET",
      dataType: "json",
      data: {
        query: query,
        query: query,
        filter_one: filter_one,
        filter_two: filter_two,
        filter_two_type: filter_two_type,
      },
      success: function (data) {
        console.log(data)
        if (data["success"] == true) {
          $("#applicationNo").val(data["data"]["Application_No"])
          $("#myAction").val(data["data"]["modify"])
          $("#leaveType").val(data["data"]["Leave_Code"])
          get_leave_balance(data["data"]["Leave_Code"])
          $("#daysAppliedRow").show()
          $("#start-date").val(data["data"]["Start_Date"])
          $("#isReturnSameDay").val(data["data"]["Return_same_day"])
          if (data["data"]["Return_same_day"] === true) {
            $("#daysAppliedRow").hide()
            $("#daysAppliedRow").prop("disabled", true)
            document.getElementById("isReturnSameDay").value = "True"
          } else {
            $("#daysAppliedRow").show()
            $("#daysAppliedRow").prop("disabled", false)
            $("#daysApplied").val(data["data"]["Days_Applied"])
            document.getElementById("isReturnSameDay").value = "False"
          }
          $next_one.removeAttr("hidden")
        } else {
        }
      },
      error: function (xhr, status, error) {
        console.log("Error:", error)
      },
    })
  }

  function Load_Attachments(pk) {
    $.ajax({
      url: "/selfservice/Attachments/" + pk + "/",
      type: "GET",
      dataType: "json",
      success: function (data) {
        var containerDiv = $("#attachments_container")
        containerDiv.empty()
        for (var i = 0; i < data.length; i++) {
          var docNo = data[i].No
          var tableID = data[i].TableID
          var attachmentID = data[i].ID
          var File_Name = data[i].FileName
          var File_Extension = data[i].FileExtension

          var attachmentDiv = $("<div>", {
            class: "col-md-4",
          })
          var fileManBoxDiv = $("<div>", {
            class: "file-man-box",
          })
          var deleteForm = $("<form>", {
            method: "POST",
          })

          deleteForm.append(
            $("<input>", {
              type: "hidden",
              name: "docID",
              value: docNo,
            })
          )
          deleteForm.append(
            $("<input>", {
              type: "hidden",
              name: "tableID",
              value: tableID,
            })
          )
          var deleteButton = $("<button>", {
            class: "file-close",
            id: "file-close",
          }).append(
            $("<i>", {
              class: "fa fa-times-circle",
            })
          )

          deleteButton.on("click", function (event) {
            event.preventDefault()
            $.ajax({
              type: "POST",
              url: "/selfservice/RemoveAttachment/",
              data: {
                docID: attachmentID,
                tableID: tableID,
                headerID: docNo,
                csrfmiddlewaretoken: $("input[name=csrfmiddlewaretoken]").val(),
              },
              success: function (data) {
                if (data["success"] == true) {
                  iziToast.show({
                    theme: "dark",
                    backgroundColor: "#239B56",
                    icon: "las la-check-circle",
                    message: data["message"],
                    position: "topRight",
                    progressBarColor: "#F4F6F7",
                  })
                  Load_Attachments(pk)
                  if (attachmentsDiv.children().length > 0) {
                    $("#attachments_row").show() // show the div if there are attachments
                  } else {
                    $("#attachments_row").hide() // hide the div if there are no attachments
                  }
                } else {
                  iziToast.show({
                    theme: "dark",
                    icon: "las la-exclamation",
                    title: "Error",
                    message: data["error"],
                    position: "topRight",
                    progressBarColor: "#ff0800",
                  })
                }
              },
              error: function (error) {
                console.log(error)
              },
            })
          })
          fileManBoxDiv.append(deleteButton)
          // create the div for the file icon
          var fileImgBoxDiv = $("<div>", {
            class: "file-img-box",
          }).append(
            $("<img>", {
              src: "../../../static/icons/approved.gif",
              alt: "icon",
            })
          )
          fileManBoxDiv.append(fileImgBoxDiv)
          // create the div for the file name
          var fileManTitleDiv = $("<div>", {
            class: "file-man-title",
          }).append(
            $("<h5>", {
              class: "mb-0 text-overflow",
            }).text(File_Name + "." + File_Extension)
          )
          fileManBoxDiv.append(fileManTitleDiv)
          attachmentDiv.append(fileManBoxDiv)
          containerDiv.append(attachmentDiv)
        }
      },
      error: function (xhr, status, error) {
        console.log("Error:", error)
      },
    })
  }

  function ApproversData(pk) {
    $.ajax({
      url: "/selfservice/ApproversData/" + pk + "/",
      type: "GET",
      dataType: "json",
      success: function (data) {
        var tableBody = $("#approvers_table tbody")
        tableBody.empty()

        for (var i = 0; i < data.length; i++) {
          var Approver_ID = data[i].ApproverID
          var Sequence_No_ = data[i].SequenceNo
          var ApproverStatus = data[i].Status
          var Last_Modified_By_User_ID = data[i].Last_Modified_By_User_ID
          var Last_Date_Time_Modified = data[i].Last_Date_Time_Modified

          var row = $("<tr>")
          row.append($("<td>").text(Approver_ID))
          row.append($("<td>").text(Sequence_No_))
          row.append($("<td>").text(ApproverStatus))
          row.append($("<td>").text(Last_Modified_By_User_ID))
          row.append(
            $("<td>").text(
              moment(Last_Date_Time_Modified, "YYYY-MM-DD").format(
                "Do MMM YYYY"
              )
            )
          )
          tableBody.append(row)
        }
        // initialize DataTables for each table
        if (!$.fn.DataTable.isDataTable("#approvers_table")) {
          $("#approvers_table").DataTable({
            pageLength: 5,
            order: [[0, "desc"]],
          })
        }
      },
      error: function (xhr, status, error) {
        console.log("Error:", error)
      },
    })
  }

  $next_one.click(function (event) {
    event.preventDefault()
    $header_step.hide()
    $attachments_step.show()
  })

  $("#Attachment_Toggle").click(function () {
    $Reliever_Form.hide(200)
    $relievers_table.hide(300)
    $Attachment_Toggle.hide(400)
    $Attachment_Prev.hide(500)
    $approvalForm.hide(600)
    $attachmentForm.show(1000)
    show_toast_with_delay()
  })

  $attachment_next.click(function (event) {
    event.preventDefault()
    $attachmentForm.hide(800)
    $Attachment_Toggle.show()
    $Attachment_Prev.show()
    $approvalForm.show()
    $attachments_step.show()
  })

  $Attachment_Prev.click(function (event) {
    event.preventDefault()
    $attachments_step.hide()
    $header_step.show()
  })

  function show_toast_with_delay() {
    setTimeout(function () {
      iziToast.show({
        theme: "dark",
        icon: "fas fa-exclamation-circle",
        title:
          'Please make sure to click "Next" after you have finished uploading the attachments or to close the attachment form.',
        position: "topRight",
        progressBarColor: "rgb(255, 255, 255)",
      })
    }, 4000)
  }
})
